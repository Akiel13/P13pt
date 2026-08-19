import P13pt.mascril.addresses as adress
import P13pt.mascril.acquire as acquire

# 🌡️ Temperature controlers 🌡️
from P13pt.drivers.si9700 import SI9700
from P13pt.drivers.tic500 import TIC500

# ⚡ Voltage sources ⚡
from P13pt.drivers.bilt import Bilt, BiltVoltageSource, BiltVoltMeter
from P13pt.drivers.yoko7651 import Yoko7651
from P13pt.drivers.keithley2400 import K2400
from P13pt.drivers.keithley2600 import K2600
from P13pt.drivers.keithley2612 import K2612

# 📻 Vector Network Analyzers 📻
from P13pt.drivers.anritsuvna import AnritsuVNA
from P13pt.drivers.rohdeschwarz_drivers.rohdeschwarz.instruments.vna import Vna as RohdeSchwarzVNA
"""
# ⚙️ Motors ⚙️
from P13pt.drivers.bsc203 import BSC203Motor
"""

import numpy as np




def initialise_temperature(measurement) :
    """🌡️ Initialization of the temperature controlers 🌡️
    
    If the measurement station is 'JANIS', the temperature controller will be
    the SI9700.
    If the measurement station is 'Cascade', it will be the TIC500
    
    
    Parameters
    ----------
    measurement : MeasurementBase (from P13pt.mascril.measurement)
        The python object representing your measurement.
    measurement_station : string
        Name of the measurement station.
        The supported names are :
            'Cascade'
            'JANIS' (on its way to deprecation)
        If the measurement station is 'JANIS', the temperature controller will
        be the SI9700.
        If the measurement station is 'Cascade', it will be the TIC500
    
    Returns
    -------
    tc : TIC500 or SI9700 (from P13pt.drivers)
        Python object for communication with the temperature controller.
        Defaults to None if the measurement station is not one of the supported names.
    """
    
    try :
        measurement_station = measurement.measurement_station
    except AttributeError :
        measurement_station = None
    
    # Initialise SI9700 temperature controler
    if measurement_station == 'JANIS' :
        try :
            print("🌡️ Setting up SI9700 temperature controller...")
            machine_adress = adress.si9700['JANIS']
            measurement.temperature_controller = SI9700(machine_adress)
            print("🌡️ Temperature controller SI9700 is set up.")
            print("------------------------------")
        except Exception as exc :
            print("⛔ There has been an error setting up the SI9700 temperature controller.")
            raise exc
    
    # Initialize TIC500 temperature controler
    elif measurement_station == 'Cascade' :
        try :
            print("🌡️ Setting up TIC500 temperature controller...")
            machine_adress = adress.tic500['Cascade']
            measurement.temperature_controller = TIC500(machine_adress)
            print("🌡️ Temperature controller TIC500 is set up.")
            print("------------------------------")
        except Exception as exc :
            print("⛔ There has been an error setting up the TIC500 temperature controller.")
            raise exc
    
    measurement.measure_temperature = lambda : acquire.measure_temperature(
            measurement.temperature_controller)
    return measurement.temperature_controller



def initialise_voltage_sources(measurement, src_Vds, src_Vg, slope_vg_vd=.5,
                               reset_instruments=True, src_Vchuck="None",
                               slope_vchuck=1) :
    """⚡ Initialisation of the voltage sources ⚡
    
    
    Parameters
    ----------
    measurement : MeasurementBase (from P13pt.mascril.measurement)
        The python object representing your measurement.
    src_Vds : string
        Name of the machine controlling the Vds voltage.
        The supported names are :
            'K2400_adress2', 'K2400_adress24', 'K2600', 'K2612',
            'K2612 channel A', 'K2612 channel B'
            & any string starting with 'Bilt'
    src_Vg : string
        Name of the machine controlling the Vg voltage.
        The supported names are :
            'K2400_adress2', 'K2400_adress24', 'K2600', 'K2612',
            'K2612 channel A', 'K2612 channel B', 'Yoko'
            & any string starting with 'Bilt'
    slope_vg_vd : float or list, optional
        Speed (in V/s) at which the machines controlling Vds & Vg are instructed to operate
        Can be a list-like object, in which case slope_vg_vd[0] is passed as the speed for Vds
            & slope_vg_vd[1] as the speed for Vg
        Defaults to 0.5 V/s if unspecified
    reset_instruments : Bool, optional
        Boolean that probably does something but I don't know what.
        Defaults to True
    src_Vchuck : string, optional
        Name of the machine controlling the Vchuck voltage.
        The supported names are :
            'K2400_adress2', 'K2400_adress24', 'K2600', 'K2612',
            'K2612 channel A', 'K2612 channel B', 'Yoko'
    slope_vg_vd : float, optional
        Speed (in V/s) at which the machine controlling Vchuck is instructed to operate
        Defaults to 1 V/s
    
    Returns
    -------
    sourceVds 
        Python object for communication with the machine controlling Vds.
        Defaults to None if the src_Vds is not one of the supported names.
    sourceVg
        Python object for communication with the machine controlling Vg.
        Defaults to None if the src_Vg is not one of the supported names.
    sourceVchuck
        Python object for communication with the machine controlling Vg.
        Defaults to None if the src_Vchuck is unspecified, or is not one of the supported names.
    """
    
    sourceVchuck = None
    sourceVds = None
    sourceVg = None
    
    # Checking if we asked for different speeds for Vg & Vds
    try :
        Vg_speed = slope_vg_vd[0]
        Vds_speed = slope_vg_vd[1]
    except TypeError :
        Vg_speed = slope_vg_vd
        Vds_speed = slope_vg_vd
    
    try :
        measurement_station = measurement.measurement_station
    except AttributeError :
        measurement_station = None
    
    # Initialise K2400_24 voltage source / ammeter
    if 'K2400_adress24' in (src_Vg, src_Vds, src_Vchuck) :
        try :
            print("⚡ Setting up K2400_24 DC source...")
            machine_adress = adress.k2400_24[measurement_station]
            if 'K2400_adress24' == src_Vg : 
                sourceVg = K2400(machine_adress, sourcemode='v', vrang=200,
                                 irang=None, slope=Vg_speed,
                                 initialise=reset_instruments)
                measurement.sourceVg = sourceVg
                measurement.meterVg = sourceVg
                measurement.meterIleak = sourceVg
            if 'K2400_adress24' == src_Vds : 
                sourceVds = K2400(machine_adress, sourcemode='v', vrang=200,
                                  irang=None, slope=Vds_speed,
                                  initialise=reset_instruments)
                measurement.sourceVds = sourceVds
                measurement.meterVds = sourceVds
                measurement.meterIds = sourceVds
            if 'K2400_adress24' == src_Vchuck : 
                sourceVchuck = K2400(machine_adress, sourcemode='v', vrang=200,
                                     irang=None, slope=slope_vchuck,
                                     initialise=reset_instruments)
                measurement.sourceVchuck = sourceVchuck
                measurement.meterVchuck = sourceVchuck
                measurement.meterIchuck = sourceVchuck
            print("⚡ K2400_24 voltage source & ammeter are set up.")
            print("------------------------------")
        except Exception as exc :
            print("⛔ There has been an error setting up K2400_24 voltage source.")
            raise exc
    
    # Initialise K2400_2
    if 'K2400_adress2' in (src_Vg, src_Vds, src_Vchuck) :
        try :
            print("⚡ Setting up K2400_02 DC source...")
            machine_adress = adress.k2400_2[measurement_station]
            if 'K2400_adress2' == src_Vg : 
                sourceVg = K2400(machine_adress, sourcemode='v', vrang=200,
                                 irang=None, slope=Vg_speed,
                                 initialise=reset_instruments)
                measurement.sourceVg = sourceVg
                measurement.meterVg = sourceVg
                measurement.meterIleak = sourceVg
            if 'K2400_adress2' == src_Vds : 
                sourceVds = K2400(machine_adress, sourcemode='v', vrang=200,
                                  irang=None, slope=Vds_speed,
                                  initialise=reset_instruments)
                measurement.sourceVds = sourceVds
                measurement.meterVds = sourceVds
                measurement.meterIds = sourceVds
            if 'K2400_adress2' == src_Vchuck : 
                sourceVchuck = K2400(machine_adress, sourcemode='v', vrang=200,
                                     irang=None, slope=slope_vchuck,
                                     initialise=reset_instruments)
                measurement.sourceVchuck = sourceVchuck
                measurement.meterVchuck = sourceVchuck
                measurement.meterIchuck = sourceVchuck
            print("K2400_02 voltage source & ammeter are set up.")
            print("------------------------------")
        except Exception as exc :
            print("⛔ There has been an error setting up K2400_02 voltage source.")
            raise exc
            
    # Initialise K2600
    if True in ['K2600' in src for src in (src_Vg, src_Vds, src_Vchuck)] :
        try :
            print("⚡ Setting up K2600 DC sources...")
            machine_adress = adress.k2600[measurement_station]
            if src_Vg in ('K2600 channel A') :
                sourceVg = K2600(machine_adress,
                                 slope=Vg_speed,
                                 initialise=reset_instruments)
                measurement.sourceVg = sourceVg
                measurement.meterVg = sourceVg
                measurement.meterIleak = sourceVg
            elif src_Vg in ('K2600', 'K2600 channel B') : 
                sourceVg = K2600(machine_adress, channel='B',
                                 slope=Vg_speed,
                                 initialise=reset_instruments)
                measurement.sourceVg = sourceVg
                measurement.meterVg = sourceVg
                measurement.meterIleak = sourceVg
            if src_Vds in ('K2600', 'K2600 channel A') :
                sourceVds = K2600(machine_adress,
                                  slope=Vds_speed,
                                  initialise=reset_instruments, reset=False)
                measurement.sourceVds = sourceVds
                measurement.meterVds = sourceVds
                measurement.meterIds = sourceVds
            elif src_Vds in ('K2600 channel B') :
                sourceVds = K2600(machine_adress, channel='B',
                                  slope=Vds_speed,
                                  initialise=reset_instruments, reset=False)
                measurement.sourceVds = sourceVds
                measurement.meterVds = sourceVds
                measurement.meterIds = sourceVds
            if src_Vchuck in ('K2600 channel A') : 
                sourceVchuck = K2600(machine_adress,
                                     slope=slope_vchuck,
                                     initialise=reset_instruments)
                measurement.sourceVchuck = sourceVchuck
                measurement.meterVchuck = sourceVchuck
                measurement.meterIchuck = sourceVchuck
            elif src_Vchuck in ('K2600', 'K2600 channel B') :
                sourceVchuck = K2600(machine_adress, channel='B',
                                     slope=slope_vchuck,
                                     initialise=reset_instruments)
                measurement.sourceVchuck = sourceVchuck
                measurement.meterVchuck = sourceVchuck
                measurement.meterIchuck = sourceVchuck
            print("⚡ K2600 voltage sources & ammeters are set up.")
            print("------------------------------")
        except Exception as exc :
            print("⛔ There has been an error setting up K2600 voltage sources.")
            raise exc
    
    ## Initialise K2612
    if True in ['K2612' in src for src in (src_Vg, src_Vds, src_Vchuck)] :
        try :
            print("⚡ Setting up K2612 DC sources...")
            machine_adress = adress.k2612[measurement_station]
            if src_Vg in ('K2612 channel A') :
                sourceVg = K2612(machine_adress,
                                 slope=Vg_speed,
                                 initialise=reset_instruments)
                measurement.sourceVg = sourceVg
                measurement.meterVg = sourceVg
                measurement.meterIleak = sourceVg
            elif src_Vg in ('K2612', 'K2612 channel B') : 
                sourceVg = K2612(machine_adress, channel='B',
                                 slope=Vg_speed,
                                 initialise=reset_instruments)
                measurement.sourceVg = sourceVg
                measurement.meterVg = sourceVg
                measurement.meterIleak = sourceVg
            if src_Vds in ('K2612', 'K2612 channel A') :
                sourceVds = K2612(machine_adress,
                                  slope=Vds_speed,
                                  initialise=reset_instruments, reset=False)
                measurement.sourceVds = sourceVds
                measurement.meterVds = sourceVds
                measurement.meterIds = sourceVds
            elif src_Vds in ('K2612 channel B') :
                sourceVds = K2612(machine_adress, channel='B',
                                  slope=Vds_speed,
                                  initialise=reset_instruments, reset=False)
                measurement.sourceVds = sourceVds
                measurement.meterVds = sourceVds
                measurement.meterIds = sourceVds
            if src_Vchuck in ('K2612 channel A') : 
                sourceVchuck = K2612(machine_adress,
                                     slope=slope_vchuck,
                                     initialise=reset_instruments)
                measurement.sourceVchuck = sourceVchuck
                measurement.meterVchuck = sourceVchuck
                measurement.meterIchuck = sourceVchuck
            elif src_Vchuck in ('K2612', 'K2612 channel B') :
                sourceVchuck = K2612(machine_adress, channel='B',
                                     slope=slope_vchuck,
                                     initialise=reset_instruments)
                measurement.sourceVchuck = sourceVchuck
                measurement.meterVchuck = sourceVchuck
                measurement.meterIchuck = sourceVchuck
            print("⚡ K2612 voltage sources & ammeters are set up.")
            print("------------------------------")
        except Exception as exc :
            print("⛔ There has been an error setting up K2612 voltage sources.")
            raise exc
    
    # Initialise YOKO
    if 'Yoko' in (src_Vg, src_Vchuck) :
        try :
            print("⚡ Setting up Yokogawa DC source...")
            machine_adress = adress.yoko[measurement_station]
            if 'Yoko' == src_Vchuck :
                sourceVchuck = Yoko7651(machine_adress,
                                        initialise=reset_instruments, rang=30,
                                        slope=slope_vchuck)
                measurement.sourceVchuck = sourceVchuck
            if 'Yoko' == src_Vg :
                sourceVg = Yoko7651(machine_adress,
                                    initialise=reset_instruments, rang=30,
                                    slope=Vg_speed)
                measurement.sourceVg = sourceVg
            print("⚡ Yokogawa voltage source is set up.")
            print("------------------------------")
        except Exception as exc :
            print("⛔ There has been an error setting up Yokogawa voltage source.")
            raise exc
    
    # Initialise BILT
    if 'Bilt' in (src_Vg[0:4], src_Vds[0:4]) :
        try :
            print("⚡ Setting up BILT DC sources and voltmeters...")
            machine_adress = adress.bilt[measurement_station]
            bilt = Bilt(machine_adress)
            port_meter = adress.position_meter_bilt[measurement_station]
            port_source = adress.position_source_bilt[measurement_station]
            if 'Bilt' == src_Vg[0:4] :
                port_Vg = src_Vg.split('_')[-1]
                sourceVg = BiltVoltageSource(bilt, port_source + port_Vg,
                                             rang = "12", filt = "1",
                                             slope = Vg_speed, label=None,
                                             initialise=reset_instruments)
                measurement.sourceVg = sourceVg
                measurement.meterVg = BiltVoltMeter(bilt,
                                                    port_meter + port_Vg,
                                                    filt = "2",
                                                    label = "Vgm")  
            if 'Bilt' == src_Vds[0:4] : 
                port_Vds = src_Vds.split('_')[-1]
                sourceVds = BiltVoltageSource(bilt, port_source + port_Vds,
                                              rang = "12", filt = "1",
                                              slope = Vds_speed, label=None,
                                              initialise=reset_instruments)
                measurement.sourceVds = sourceVds
                measurement.meterVds = BiltVoltMeter(bilt,
                                                     port_meter + port_Vds,
                                                     filt = "2",
                                                     label = "Vdsm")
            print("⚡ BILT voltage sources and voltmeters are set up.")
            print("------------------------------")
        except Exception as exc :
            print("⛔ There has been an error setting up BILT voltage source.")
            raise exc
            
    return sourceVds, sourceVg, sourceVchuck
