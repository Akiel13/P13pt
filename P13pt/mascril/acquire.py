"""
A collection of higher-level functions to ask machines to perform some tasks.
Those used to be redefined identically in most Measurement objects, so grouping them
in a submodule might just be an efficiency gain.
"""
import threading





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



def get_Vds_Vg_Vchuck(measurement) :
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





def get_Ids_Ileak_Ichuck(measurement) :
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
    return T
    
        
