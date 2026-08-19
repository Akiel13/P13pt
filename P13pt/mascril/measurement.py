from __future__ import print_function
import sys
import os
import time
import json
import tarfile
import traceback
import numpy as np
from io import BytesIO as StringIO
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from P13pt.mascril.parameter import MeasurementParameter
from P13pt.utils.file_management import create_folder
import P13pt.mascril.acquire as acquire
import P13pt.mascril.initialisation_instruments as instruments

try:
    from PyQt5.QtCore import QString
except ImportError:
    QString = str


class MeasurementBaseBase(QThread) :

    ALARM_SHOWVALUE = 0     # does nothing, but the user will see the result of the expression (this way we are not
                            # limited to boolean expressions, we can even use the "alarms" to do real-time calculations
                            # with the observables

    ALARM_QUIT = 1          # quit the acquisition if the alarm condition is True

    ALARM_CALLCOPS = 2      # show a colour indicator / a message if the alarm condition is True


    new_observables_data = pyqtSignal(list)
    new_console_data = pyqtSignal(QString)
    new_alarm_data = pyqtSignal(list)

    params = {} # Dictionnary of measurement parameters
    observables = [] # List of variables to be saved and kept track of
    alarms = []

    def __init__(self, redirect_console=False, parent=None) :
        super(MeasurementBaseBase, self).__init__(parent)
        self.redirect_console = redirect_console
        self.flags = {'quit_requested': False}
        self.data_file = None

    def run(self):
        if self.redirect_console:
            # The following has to be in the run function so that it is executed
            # in its own thread, otherwise sys is not the same.
            self.std_sav = sys.stdout, sys.stderr
            sys.stdout = sys.stderr = self.sio = StringIO()
            self.sio.write = self.new_console_data.emit
        
        # evaluate the parameters dictionary
        params = self.evaluate_params()
        timestamp = time.strftime('%d/%m %H:%M:%S')
        print("░░░░░░░░")
        print("**************************************************")
        print(f"{timestamp} : Starting acquisition script")
        print("=============================================")
        
        # Performing the acquisition
        try :
            self.measure(**params)
        except :
            timestamp = time.strftime('%d/%m %H:%M:%S')
            print(f"{timestamp} : Error 💣 💣 💣  ")
            print("The following exception occured during the acquisition")
            print("↓")
            print("------------------------------")
            traceback.print_exc(file=sys.stdout)
            print("------------------------------")
            time.sleep(4)
        
        # Performing the clean-up
        try :
            self.tidy_up()
        except :
            timestamp = time.strftime('%d/%m %H:%M:%S')
            print(f"{timestamp} : Error 💀 💀 💀  ")
            print("The following exception occured during the clean-up")
            print("↓")
            print("------------------------------")
            traceback.print_exc(file=sys.stdout)
        
        # End
        timestamp = time.strftime('%d/%m %H:%M:%S')
        print("=============================================")
        print(f"{timestamp} : Ending acquisition script")
        print("**************************************************")
        print("░░░░░░░░")
        self.reset_console()
    
    def evaluate_params(self):
        params = {}
        for key in self.params:
            if isinstance(self.params[key], MeasurementParameter):
                params[key] = self.params[key].value
            else:
                params[key] = self.params[key]
        return params

    def evaluate_alarms(self, locals) :
        locals['np'] = np
        alarm_data = [0]*len(self.alarms)
        for i,alarm in enumerate(self.alarms) :
            condition = alarm[0]
            action = alarm[1]
            if condition.strip() == '' :
                continue
            try:
                result = eval(condition, locals)
            except Exception as exc :
                if not self.redirect_console :
                    print(f"Alarm could not be evaluated: {condition}", end="")
                    print(" / error: "+str(exc))
                alarm_data[i] = exc
            else:
                if action == self.ALARM_SHOWVALUE :
                    if not self.redirect_console :
                        print(condition+' =', result)
                    alarm_data[i] = result
                elif action == self.ALARM_CALLCOPS :
                    if result:
                        if not self.redirect_console :
                            print('Calling the cops: '+condition)
                        alarm_data[i] = True
                elif action == self.ALARM_QUIT:
                    if result:
                        if not self.redirect_console :
                            print('Stopping the acquisition: '+condition)
                        alarm_data[i] = True
                        self.quit()
        self.new_alarm_data.emit(alarm_data)
    
    def prepare_saving(self, filename):
        # A couple of safety checks
        if self.data_file is not None :
            raise Exception("The last data file has not been properly closed.")
        directory = os.path.dirname(filename)
        create_folder(directory)
        # Creating the save file
        self.filename = filename
        self.data_file = open(filename, 'a')
        self.data_file.write('#' + '\t'.join(self.observables) + '\n')
        # Retrieving the experimental conditions
        params = self.evaluate_params()
        params["filename"] = self.filename.split("\\")[-1].split(".")[0]
        for key in params.keys() :
            if isinstance(params[key], np.ndarray) :
                params[key] = params[key].tolist()
        # Writing the experimental conditions in a companion file
        directory = os.path.dirname(self.filename)
        companion_filename = os.path.join(directory,
                                          "experimental_conditions.json")
        with open(companion_filename, 'w') as companion_file :
            json.dump(params, companion_file)
        companion_file.close()
        tarfile.open(f"{self.filename.split('.')[0]}.tar.gz", 'x:gz')

    def save_row(self, locals):
        if self.data_file is None:
            raise Exception("No data file has been opened.")
        row = []
        for obs in self.observables:
            try:
                value = locals[obs]
            except KeyError:
                value = None
            row.append(value)
        self.data_file.write('\t'.join([str(v) for v in row]) + '\n')       
        self.data_file.flush()
        self.new_observables_data.emit(row)
        self.evaluate_alarms(locals)

    def end_saving(self):
        # Properly close the file
        if self.data_file is not None:
            self.data_file.close()
        self.data_file = None
        # Combine the main & companion files into an archive
        try :
            directory = os.path.dirname(self.filename)
            companion_filename = os.path.join(directory,
                                              "experimental_conditions.json")
            archive = tarfile.open(self.filename.split(".")[0]+".tar.gz",
                                   'w:gz')
            for file in [self.filename, companion_filename] :
                archive.add(file, arcname=file.split("\\")[-1])
            archive.close()
        except AttributeError :
            traceback.print_exc(file=sys.stdout)

    def measure(self, **kwargs):
        """The function to be called in order to perform the measurement"""
        print("Blank measurement")

    def reset_console(self):
        if self.redirect_console:
            sys.stdout, sys.stderr = self.std_sav
            self.sio.close()

    @pyqtSlot()
    def quit(self):
        self.flags['quit_requested'] = True

    @pyqtSlot()
    def terminate(self):
        self.reset_console()
        if self.data_file:
            self.data_file.close()
            self.data_file = None
        super(MeasurementBaseBase, self).terminate()
    
    def tidy_up(self):
        self.end_saving()
        
        try :
            self.sourceVds.set_voltage(0.)
            print("------------------------------")
            print("Vds set to zero")
        except AttributeError :
            # The AttributeErrors happen if a voltage source is set to None
            # In which case there is not voltage to set to 0 so we can proceed
            pass
        try :
            self.sourceVg.set_voltage(0.)
            print("------------------------------")
            print("Vg set to zero")
        except AttributeError :
            pass
        try :
            self.sourceVchuck.set_voltage(0.)
            print("------------------------------")
            print("Vchuck set to zero")
        except AttributeError :
            pass















class MeasurementBase(MeasurementBaseBase) :
    
    initialise_vna = instruments.initialise_vna
    initialise_lockin = instruments.initialise_lockin
    initialise_temperature = instruments.initialise_temperature
    initialise_voltage_sources = instruments.initialise_voltage_sources
    
    set_Vds_Vg_Vchuck = acquire.set_Vds_Vg_Vchuck
    measure_Vds_Vg_Vchuck = acquire.measure_Vds_Vg_Vchuck
    measure_Ids_Ileak_Ichuck = acquire.measure_Ids_Ileak_Ichuck
    
    
    def __init__(self, redirect_console=False, parent=None) :
        super(MeasurementBase, self).__init__(
          redirect_console=redirect_console,
          parent=parent,
          )
        self.measurement_station = None
    
    def tidy_up(self):
        # Properly save the data
        self.end_saving()
        try :
            dirname = os.path.dirname(self.filename)
            print(f"✅ Measurement data saved in :\n{dirname}")
            print(f"{self.filename.split(dirname)[1]}")
        except AttributeError : print("✅ Measurement data saved")
        
        # Set voltages to 0
        self.set_Vds_Vg_Vchuck(Vds=0, Vg=0, Vchuck=0)
        try :
            self.sourceVds.set_voltage(0.)
            print("------------------------------")
            print("Vds set to zero")
        except AttributeError :
            pass
        try :
            self.sourceVg.set_voltage(0.)
            print("------------------------------")
            print("Vg set to zero")
        except AttributeError :
            pass
        try :
            self.sourceVchuck.set_voltage(0.)
            print("------------------------------")
            print("Vchuck set to zero")
        except AttributeError :
            pass
