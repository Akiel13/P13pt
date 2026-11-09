"""
A collection of higher-level functions to ask machines to perform some tasks.
Those used to be redefined identically in most Measurement objects, so grouping them
in a submodule might just be an efficiency gain.
"""


import os
import time
import threading
import numpy as np


from P13pt.utils.file_management import (without_accents,
                                         without_characters_forbidden_in_a_filename)
from P13pt.mascril.waiting import wait
from math import floor


try : 
    from P13pt.drivers.si9700 import SI9700
except ImportError :
    class SI9700 :
        pass

try : 
    from P13pt.drivers.si9700 import TIC500
except ImportError :
    class TIC500 :
        pass





def measure_Vds_Vg_Vchuck(measurement) :
    # List of the voltmeters we want to use
    voltmeter_roles = ["meterVds", "meterVg", "meterVchuck"]
    
    # Check which voltmeters are actually present
    voltmeters = {}
    for j, role in enumerate(voltmeter_roles) :
        try :
            meter = getattr(measurement, role)
        except AttributeError :
            continue
        if meter is None :
            continue
        voltmeters[j] = meter

    # Wrap the acquisition function for each voltmeter
    measured_voltages = [None for role in voltmeter_roles]
    def measure_voltage(index) :
        measured_voltages[index] = voltmeters[index].get_voltage()

    # Checks if it should multithread
    try :
        multithread_mode = measurement.threading_optimisations
    except AttributeError :
        multithread_mode = False

    # If not : just ask each voltmeter one by one
    if not multithread_mode :
        for k in voltmeters.keys() :
            measure_voltage(k)
        return measured_voltages
        
    # Sort the voltmeters per machine
    machines = {}
    for j in voltmeters.keys() :
        meter = voltmeters[j]
        if meter.adress in machines.keys() :
            machines[meter.adress].append(j)
        else :
            machines[meter.adress] = [j]
    
    # Define one thread per machine
    threads = []
    for machine in machines.keys() :
        t = threading.Thread(
          target=lambda x : [measure_voltage(meter) for meter in machines[x]],
          args=(machine,)
          )
        threads.append(t)
    
    # Start each thread
    for t in threads :
        t.start()

    # Wait for all threads to finish
    for t in threads :
        t.join()
    
    return measured_voltages




def measure_Ids_Ileak_Ichuck(measurement) :
    # List of the ammeters we want to use
    ammeter_roles = ["meterIds","meterIleak","meterIchuck"]
    
    # Check which ammeters are actually present
    ammeters = {}
    for j, role in enumerate(ammeter_roles) :
        try :
            meter = getattr(measurement, role)
        except AttributeError :
            continue
        if meter is None :
            continue
        ammeters[j] = meter

    # Define what each ammeter should do
    measured_currents = [None for role in ammeter_roles]
    def measure_current(index) :
        measured_currents[index] = ammeters[index].get_current()

    # Checks if it should multithread
    try :
        multithread_mode = measurement.threading_optimisations
    except AttributeError :
        multithread_mode = False

    # If not : just ask each voltmeter one by one
    if not multithread_mode :
        for k in ammeters.keys() :
            measure_current(k)
        return measured_currents
        
    # Sort the ammeters per machine
    machines = {}
    for j in ammeters.keys() :
        meter = ammeters[j]
        if meter.adress in machines.keys() :
            machines[meter.adress].append(j)
        else :
            machines[meter.adress] = [j]
    
    # Define one thread per machine
    threads = []
    for machine in machines.keys() :
        t = threading.Thread(
          target=lambda x : [measure_current(meter) for meter in machines[x]],
          args=(machine,)
          )
        threads.append(t)
    
    # Start each thread
    for t in threads :
        t.start()

    # Wait for all threads to finish
    for t in threads :
        t.join()
    
    return measured_currents




def set_Vds_Vg_Vchuck(measurement, Vds=None, Vg=None, Vchuck=None) :
    # List of the sources we want to use
    source_roles = ["sourceVds","sourceVg","sourceVchuck"]
    voltages = [Vds, Vg, Vchuck]
    
    # Check which sources are actually present
    sources = {}
    for j, role in enumerate(source_roles) :
        if voltages[j] is None :
            continue
        try :
            source = getattr(measurement, role)
        except AttributeError :
            continue
        if source is None :
            continue
        sources[j] = source

    # Define what each source should do
    def apply_voltage(index) :
        sources[index].set_voltage(voltages[index])

    # Checks if it should multithread
    try :
        multithread_mode = measurement.threading_optimisations
    except AttributeError :
        multithread_mode = False

    # If not : just ask each source one by one
    if not multithread_mode :
        for k in sources.keys() :
            apply_voltage(k)
        return None
        
    # Sort the sources per machine
    machines = {}
    for j in sources.keys() :
        source = sources[j]
        if source.adress in machines.keys() :
            machines[source.adress].append(j)
        else :
            machines[source.adress] = [j]
    
    # Define one thread per machine
    threads = []
    for machine in machines.keys() :
        t = threading.Thread(
          target=lambda a : [apply_voltage(i) for i in machines[a]],
          args=(machine,)
          )
        threads.append(t)
    
    # Start each thread
    for t in threads :
        t.start()

    # Wait for all threads to finish
    for t in threads :
        t.join()



        
def measure_temperature(tempertautre_controller, *args, **kwargs) :
    """
    Measures the temperature.
    
    Parameters
    ----------
    tc : TIC500 or SI9700 (from P13pt.drivers)
        Python object for communication with the temperature controller.
    
    Returns
    -------
    T : number
        Value of the temperature in kelvins.
        Is None if tc is not a SI9700 or a TIC500 object
    """
    T = None
    if isinstance(tempertautre_controller, SI9700):
        Ta = tempertautre_controller.get_temp('a')
        Tb = tempertautre_controller.get_temp('b')
        T = (Ta + Tb)/2
    elif isinstance(tempertautre_controller, TIC500):
        T = tempertautre_controller.get_temp('Chuck')
    return T



def measure_lockin_signal(lockin, iterations=2) :
    X_list = []
    Y_list = []
    for _ in range(iterations):
        wait(0.5)
        X_list.append(np.float(lockin.query('X1.?')))
        lockin.query('X1.?')
        Y_list.append(np.float(lockin.query('Y1.?')))
        lockin.query('Y1.?')
        
    signal_X = np.average(X_list)
    signal_Y = np.average(Y_list)
    signal_R = np.sqrt(signal_X**2 + signal_Y**2)
    
    return signal_X, signal_Y, signal_R




    """
    In a system with 3 electrodes (the source, drain & gate), measures the
    drain-source current (Ids), as well as the gate-source current (Ileak).
    
    Parameters
    ----------
    measurement : MeasurementBase (from P13pt.mascril.measurement)
        The python object representing your measurement.
        Can also be any object with a sourceVds & a sourceVg attributes.
    src_Vds : string
        Name of the machine performing the Ids current measurement.
        The supported names are :
            'K2400_adress2', 'K2400_adress24', 'K2600', 'K2612', 'K2612 channel A', 'K2612 channel B'
            & any string starting with 'Bilt'
        If it is a string starting with 'Bilt', the measurement should have
        a Rds_Bilt_Only attribute (because the bilt is a voltmeter).
    src_Vg : string
        Name of the machine performing the Ileak current measurement.
        The supported names are :
            'K2400_adress2', 'K2400_adress24', 'K2600', 'K2612', 'K2612 channel A', 'K2612 channel B'
            & any string starting with 'Bilt'
        If it is a string starting with 'Bilt', the measurement should have
        a Rg_Bilt_Only attribute (because the bilt is a voltmeter).
    Vds : number
        The value of the drain-source voltage, in volts.
    Vg : number, optional
        The value of the gate-source voltage, in volts. Unused in the code if
        the src_Vds does not start with 'Bilt', but gets printed anyways.
    
    Returns
    -------
    Ids : number
        Value of the drain-source current, in amperes.
        Defaults to None if src_Vds was not one of the supported names.
    Rds : number
        Value of the drain-source resistance : Rds = Vds ÷ Ids
        Defaults to None if src_Vds was not one of the supported names.
    Ileak : number
        Value of the gate-source current, in amperes.
        Defaults to None if src_Vg was not one of the supported names.
    Vdsm : number
        Value of the drain-source voltage measured by the Bilt, in volts.
        Defaults to None if src_Vds was not starting by 'Bilt'
    Vgm : number
        Value of the gate-source voltage measured by the Bilt, in volts.
        Defaults to None if src_Vds was not starting by 'Bilt'
    """





def measure_oscillo_noise(scope, oscillo_acq_time, csv_filename, center=5.5e9, span=9e9, data_dir=None) :
    """
    Makes the oscilloscope perform a measurement on the range [center - ½span ; center + ½span]
    
    Parameters
    ----------
    scope : 
        Python object for communication with the oscilloscope.
    oscillo_acq_time : float
        Duration (in seconds) of the acquisition by the oscilloscope.
    csv_filename : string
        Filename under which the acquired data is to be saved.
    center : float, optional
        Frequency (in Hz) at the center of the acquisition range
        Default value is 5 GHz
    span : float, optional
        Frequency range of the acquisition (in Hz)
        Default value is 9 GHz
        Measurement will be on the frequency range [center - ½span ; center + ½span]
    data_dir : string, optional
        File path.
        If included, will save a copy of the measured data at the specified location.
    """
    
    # Format properly the range value of the measurement
    center_exponent = floor(np.log10(center))
    center_mantisse = center * 10**-center_exponent
    
    span_exponent = floor(np.log10(span))
    span_mantisse = span * 10**-span_exponent

    scope.write('CH1:COUPLING DC')
    
    # We clear the registered acquisitions by changing the value.
    scope.write(f'MATH1:SPECTRAL:CENTER {center_mantisse+.7:.4f}E{center_exponent}')    #verify the range for the oscillo
    wait(1)
    
    # Acquisition setup
    scope.write(f'MATH1:SPECTRAL:CENTER {center_mantisse:.4f}E{center_exponent}')
    scope.write(f'MATH1:SPECTRAL:SPAN {span_mantisse:.4f}E{span_exponent}')
    
    # Run
    scope.write('ACQUIRE:STATE RUN') #Essentially the oscillo is in run state, but after a maths average (in oscillo) number of acq, new acq exp dampened 
    wait(oscillo_acq_time)
    
    # Save
    timestr = time.strftime("%Y%m%d-%H%M%S")
    scope.write('SAVE:WAVEFORM:FILEFORMAT SPREADSHEETCsv')
    # Do something about the characters forbidden in a filename : / \ : " ? * > < |
    csv_filename = without_characters_forbidden_in_a_filename(csv_filename)
    csv_filename = without_accents(csv_filename)
    if len(csv_filename) > 50 : # The oscillo has a cap on filename length
        csv_filename = csv_filename[:50]
    scope.write(f'SAVE:WAVEFORM MATH1, "{timestr}_{csv_filename}.csv"')
    wait(2)
    
    # End
    scope.write('CH1:COUPLING DC')
    scope.write('ACQUIRE:STATE STOP')
    
    # bonus part - not working (?)
    data_dir = None
    if data_dir is not None :
        print("Retrieving data ?")
        data = scope.query(rf"MMEM:TRAN? 'C:\Users\Tek_local_admin\Tektronix\TekScope\Waveforms\{timestr}_{csv_filename}.csv'")
        with open(rf"{data_dir}\{csv_filename}.csv", 'w') as fp :
            fp.write(data)
            fp.close()
        print("data retrieved")






def measure_VNA_data(src_vna, vna, spectra_fol, Vds, Vg) :
    # Start a sweep
    if src_vna.lower() == 'zva67':
        channel_1 = vna.channel(1)
        vna_time = channel_1.total_sweep_time_ms / 1e3
        is_sweep_done = channel_1.isdone_nonblocking_sweep
        channel_1.start_nonblocking_sweep()
    elif src_vna.lower() == 'anritsu':
        vna_time = vna.get_sweep_time()
        is_sweep_done = vna.is_sweep_done
        vna.single_sweep(wait=False)
    else :
        return None
    print("📶 Getting VNA spectra...")
    wait(vna_time) # sleep + display sweep progress
    
    # make sure sweep is really done
    while not is_sweep_done():
        wait(0.5)
    print("🆗 Spectra done")
    
    # Filename
    timestamp = time.strftime('%Y-%m-%d_%Hh%Mm%Ss')
    spectrum_file = timestamp+'_Vg=%2.4f'%(Vg)+'_Vds=%2.4f'%(Vds)
    spectrum_filepath = os.path.join(spectra_fol, spectrum_file+'.s2p')
    
    # Saving
    if src_vna.lower() == 'zva67':
        channel_1.save_nonblocking_sweep(spectrum_filepath, (1,2))
    elif src_vna.lower() == 'anritsu':
        table = vna.get_table(range(1,5))
        np.savetxt(spectrum_filepath, np.transpose(table), header='  HZ   S   RI   R     50.00 ')
    return None


    # Another version of this code for zva67
    if src_vna == 'zva67':
        # save VNA data
        print("Getting VNA spectra...")
        vna.write('INIT1:IMM')
        vna.write('CALC1:DATA:NSW:FIRS? SDAT, 1')
        # make sure sweep is really done
        # display sweep progress
        timestamp = time.strftime('%Y-%m-%d_%Hh%Mm%Ss')
        spectrum_file = timestamp+'_Vg=%2.4f'%(Vg)+'_Vds=%2.4f'%(Vds)
        spectrum_file = os.path.join(spectra_fol, spectrum_file+'.s2p')
        vna.write("MMEM:STOR:TRAC:CHAN 1, spectrum_file")
    return None
    # Yet another version for zva67
    if src_vna == 'zva67':
        # save VNA data
        print("Getting VNA spectra...")
        vna.write(':INIT1:CONT ON')
        wait(vna_time) # 15 seconds !?!?
        timestamp = time.strftime('%Y-%m-%d_%Hh%Mm%Ss')
        spectrum_file =timestamp+'_Vg=%2.4f'%(Vg)+'_Vds=%2.4f'%(Vds)+'.s2p'
        scpi="MMEM:STOR:TRAC:CHAN 1, '{0}'"
        scpi=scpi.format(spectrum_file)
        vna.write(scpi)
    # I dont't really know which of those versions is best.
    return None
