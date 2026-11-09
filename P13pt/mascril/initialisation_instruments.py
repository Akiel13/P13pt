import P13pt.mascril.adresses as adress
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
import os




def initialise_temperature(measurement, verbose=False) :
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
    
    measurement.temperature_controller = None
    
    # Initialise SI9700 temperature controler
    if measurement_station == 'JANIS' :
        try :
            print("🌡️ Setting up SI9700 temperature controller...")
            machine_adress = adress.si9700['JANIS']
            measurement.temperature_controller = SI9700(machine_adress)
            print("🌡️ Temperature controller SI9700 is set up.")
            print("----------------------------------------")
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
            print("----------------------------------------")
        except Exception as exc :
            print("⛔ There has been an error setting up the TIC500 temperature controller.")
            raise exc
    
    measurement.measure_temperature = lambda : acquire.measure_temperature(
            measurement.temperature_controller)
    return measurement.temperature_controller



def initialise_voltage_sources(measurement, src_Vds, src_Vg,
                               Vds_speed=.5, Vg_speed=.5,
                               reset_instruments=True,
                               src_Vchuck="None", Vchuck_speed=1,
                               verbose=False) :
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
    
    try :
        measurement_station = measurement.measurement_station
    except AttributeError :
        measurement_station = None
    
    
    # Initialise K2400_24 voltage source / ammeter
    if True in ['K2400' in src for src in (src_Vg, src_Vds, src_Vchuck) if not src.endswith("2")] :
        try :
            print("⚡ Setting up K2400 DC source...")
            machine_adress = adress.k2400[measurement_station]
            if 'K2400' in src_Vg and not src_Vg.endswith("2") : 
                sourceVg = K2400(machine_adress, sourcemode='v', vrang=200,
                                 irang=None, slope=Vg_speed,
                                 initialise=reset_instruments)
                measurement.sourceVg = sourceVg
                measurement.meterVg = sourceVg
                measurement.meterIleak = sourceVg
            if 'K2400' in src_Vds and not src_Vds.endswith("2") : 
                sourceVds = K2400(machine_adress, sourcemode='v', vrang=200,
                                  irang=None, slope=Vds_speed,
                                  initialise=reset_instruments)
                measurement.sourceVds = sourceVds
                measurement.meterVds = sourceVds
                measurement.meterIds = sourceVds
            if 'K2400' in src_Vchuck and not src_Vchuck.endswith("2") : 
                sourceVchuck = K2400(machine_adress, sourcemode='v', vrang=200,
                                     irang=None, slope=Vchuck_speed,
                                     initialise=reset_instruments)
                measurement.sourceVchuck = sourceVchuck
                measurement.meterVchuck = sourceVchuck
                measurement.meterIchuck = sourceVchuck
            print("⚡ K2400 voltage source & ammeter are set up.")
            print("----------------------------------------")
        except Exception as exc :
            print("⛔ There has been an error setting up K2400_24 voltage source.")
            raise exc
    
    # Initialise K2400_2
    if True in ['K2400' in src for src in (src_Vg, src_Vds, src_Vchuck) if not src.endswith("2")] :
        try :
            print("⚡ Setting up second K2400 DC source...")
            machine_adress = adress.k2400_2[measurement_station]
            if 'K2400' in src_Vg and src_Vg.endswith("2") : 
                sourceVg = K2400(machine_adress, sourcemode='v', vrang=200,
                                 irang=None, slope=Vg_speed,
                                 initialise=reset_instruments)
                measurement.sourceVg = sourceVg
                measurement.meterVg = sourceVg
                measurement.meterIleak = sourceVg
            if 'K2400' in src_Vds and src_Vds.endswith("2") : 
                sourceVds = K2400(machine_adress, sourcemode='v', vrang=200,
                                  irang=None, slope=Vds_speed,
                                  initialise=reset_instruments)
                measurement.sourceVds = sourceVds
                measurement.meterVds = sourceVds
                measurement.meterIds = sourceVds
            if 'K2400' in src_Vchuck and src_Vchuck.endswith("2") : 
                sourceVchuck = K2400(machine_adress, sourcemode='v', vrang=200,
                                     irang=None, slope=Vchuck_speed,
                                     initialise=reset_instruments)
                measurement.sourceVchuck = sourceVchuck
                measurement.meterVchuck = sourceVchuck
                measurement.meterIchuck = sourceVchuck
            print("Second K2400 voltage source & ammeter are set up.")
            print("----------------------------------------")
        except Exception as exc :
            print("⛔ There has been an error setting up K2400_02 voltage source.")
            raise exc
            
    # Initialise K2600
    if True in ['K2600' in src for src in (src_Vg, src_Vds, src_Vchuck)] :
        try :
            print("⚡ Setting up K2600 DC sources...")
            machine_adress = adress.k2600[measurement_station]
            if 'K2600' in src_Vg and (src_Vg.endswith("A") or "channel a" in src_Vg.lower()) :
                sourceVg = K2600(machine_adress, channel='A',
                                 slope=Vg_speed,
                                 initialise=reset_instruments)
                measurement.sourceVg = sourceVg
                measurement.meterVg = sourceVg
                measurement.meterIleak = sourceVg
            elif 'K2600' in src_Vg : 
                sourceVg = K2600(machine_adress, channel='B',
                                 slope=Vg_speed,
                                 initialise=reset_instruments)
                measurement.sourceVg = sourceVg
                measurement.meterVg = sourceVg
                measurement.meterIleak = sourceVg
            if 'K2600' in src_Vds and (src_Vchuck.endswith("B") or "channel b" in src_Vds.lower()) :
                sourceVds = K2600(machine_adress, channel='B',
                                  slope=Vds_speed, 
                                  initialise=reset_instruments, reset=False)
                measurement.sourceVds = sourceVds
                measurement.meterVds = sourceVds
                measurement.meterIds = sourceVds
            elif 'K2600' in src_Vds :
                sourceVds = K2600(machine_adress, channel='A',
                                  slope=Vds_speed,
                                  initialise=reset_instruments, reset=False)
                measurement.sourceVds = sourceVds
                measurement.meterVds = sourceVds
                measurement.meterIds = sourceVds
            if 'K2600' in src_Vchuck and (src_Vchuck.endswith("A") or "channel a" in src_Vchuck.lower()) :
                sourceVchuck = K2600(machine_adress, channel='A',
                                     slope=Vchuck_speed,
                                     initialise=reset_instruments)
                measurement.sourceVchuck = sourceVchuck
                measurement.meterVchuck = sourceVchuck
                measurement.meterIchuck = sourceVchuck
            elif 'K2600' in src_Vchuck : 
                sourceVchuck = K2600(machine_adress, channel='B',
                                     slope=Vchuck_speed,
                                     initialise=reset_instruments)
                measurement.sourceVchuck = sourceVchuck
                measurement.meterVchuck = sourceVchuck
                measurement.meterIchuck = sourceVchuck
            print("⚡ K2600 voltage sources & ammeters are set up.")
            print("----------------------------------------")
        except Exception as exc :
            print("⛔ There has been an error setting up K2600 voltage sources.")
            raise exc
    
    ## Initialise K2612
    if True in ['K2612' in src for src in (src_Vg, src_Vds, src_Vchuck)] :
        try :
            print("⚡ Setting up K2612 DC sources...")
            machine_adress = adress.k2612[measurement_station]
            if 'K2612' in src_Vg and (src_Vg.endswith("A") or "channel a" in src_Vg.lower()) :
                sourceVg = K2612(machine_adress,
                                 slope=Vg_speed,
                                 initialise=reset_instruments)
                measurement.sourceVg = sourceVg
                measurement.meterVg = sourceVg
                measurement.meterIleak = sourceVg
            elif 'K2612' in src_Vg : 
                sourceVg = K2612(machine_adress, channel='B',
                                 slope=Vg_speed,
                                 initialise=reset_instruments)
                measurement.sourceVg = sourceVg
                measurement.meterVg = sourceVg
                measurement.meterIleak = sourceVg
            if 'K2612' in src_Vds and (src_Vchuck.endswith("B") or "channel b" in src_Vds.lower()) :
                sourceVds = K2612(machine_adress, channel='B',
                                  slope=Vds_speed,
                                  initialise=reset_instruments, reset=False)
                measurement.sourceVds = sourceVds
                measurement.meterVds = sourceVds
                measurement.meterIds = sourceVds
            elif 'K2612' in src_Vds :
                sourceVds = K2612(machine_adress,
                                  slope=Vds_speed,
                                  initialise=reset_instruments, reset=False)
                measurement.sourceVds = sourceVds
                measurement.meterVds = sourceVds
                measurement.meterIds = sourceVds
            if 'K2612' in src_Vchuck and (src_Vchuck.endswith("A") or "channel a" in src_Vchuck.lower()) :
                sourceVchuck = K2612(machine_adress,
                                     slope=Vchuck_speed,
                                     initialise=reset_instruments)
                measurement.sourceVchuck = sourceVchuck
                measurement.meterVchuck = sourceVchuck
                measurement.meterIchuck = sourceVchuck
            elif 'K2612' in src_Vchuck : 
                sourceVchuck = K2612(machine_adress, channel='B',
                                     slope=Vchuck_speed,
                                     initialise=reset_instruments)
                measurement.sourceVchuck = sourceVchuck
                measurement.meterVchuck = sourceVchuck
                measurement.meterIchuck = sourceVchuck
            print("⚡ K2612 voltage sources & ammeters are set up.")
            print("----------------------------------------")
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
                                        slope=Vchuck_speed)
                measurement.sourceVchuck = sourceVchuck
            if 'Yoko' == src_Vg :
                sourceVg = Yoko7651(machine_adress,
                                    initialise=reset_instruments, rang=30,
                                    slope=Vg_speed)
                measurement.sourceVg = sourceVg
            print("⚡ Yokogawa voltage source is set up.")
            print("----------------------------------------")
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
            print("----------------------------------------")
        except Exception as exc :
            print("⛔ There has been an error setting up BILT voltage source.")
            raise exc
            
    return sourceVds, sourceVg, sourceVchuck



def initialise_motors(measurement, reset_instruments=True) :
    three_axis = 0#BSC203Motor()
    if reset_instruments :
        three_axis.home_x()
        three_axis.home_y()
        three_axis.home_z()
    return three_axis



def prepare_vna_saving(measurement, src_vna, filepath) :
    vna = measurement.vna
    vna_time = 0
    if src_vna.lower() == 'zva67':
        vna_channel_1 = vna.channel(1)
        vna_pow = np.unique(np.asarray(vna_channel_1.get_frequency_segments())[:,5])
        if len(vna_pow) == 1 :
            vna_pow = vna_pow[0]
        vna_time = vna_channel_1.total_sweep_time_ms / 1e3
        vna_channel_1.save_frequency_segments(os.path.join(filepath, 'VNAconfig'))
    elif src_vna.lower() == 'anritsu':
        port1att = vna.get_source_att(1)
        port2att = vna.get_source_att(2)
        if port1att == port2att :
            vna_pow -= port1att
        vna_time = vna.get_sweep_time()
        with open(os.path.join(filepath, 'VNAconfig'),'w') as f:
            vna.dump_freq_segments(f)
    return vna_time


def initialise_vna(measurement, src_vna, reset_instruments=True, **kwargs) :    
    """📻 Initialisation of Vector Network Analyzers 📻
    
    Supported machines :
        'zva67'
        'anritsu'
    
    returns both a a python object that allows communication with the machine &
    the power (if a valid machine was specified ; otherwise returns None twice)
    """
    
    vna = None
    vna_pow = None
    
    try :
        measurement_station = measurement.measurement_station
    except AttributeError :
        measurement_station = None

    # Initialise VNA ZVA67
    if src_vna.lower() == 'zva67' :
        try :
            print("📻 Setting up VNA ZVA67")
            machine_adress = adress.zva67[measurement_station]
            measurement.vna = vna = RohdeSchwarzVNA()
            vna.open('TCPIP', machine_adress)
            
            c1 = vna.channel(1)
            c1.init_nonblocking_sweep((1,2))
            
            if not c1.is_corrected() :
                raise Exception('Please calibrate or switch on correction.')
            if c1.sweep_type != 'SEGM':
                raise Exception('Please use segmented frequency sweep')
            
            # check if the RF power is the same on both ports and for all
            # frequency segments
            vna_pow = np.unique(np.asarray(c1.get_frequency_segments())[:,5])
            if len(vna_pow) > 1 :
                raise Exception("Please select the same power for all ports and frequency segments")
            vna_pow = vna_pow[0]
            if c1.is_auto_attenuator(1) or c1.is_auto_attenuator(2) :
                raise Exception("Please do not use automatic attenuators")
            port1att = c1.get_attenuator(1)
            if port1att == c1.get_attenuator(2) :
                vna_pow -= port1att
            else:
                raise Exception("Please select the same attenuators for both ports")
            
            print("📻 VNA ZVA67 is set up.")
            print("----------------------------------------")
        except Exception as exc :
            print("⛔ There has been an error setting up VNA ZVA67.")
            raise exc
        
    # Initialise VNA ANRITSU
    elif src_vna.lower() == 'anritsu' :
        try :
            print("📻 Setting up ANRITSU VNA")
            machine_adress = adress.zva67[measurement_station]
            vna = AnritsuVNA(machine_adress)
            
            if vna.get_sweep_type() != 'FSEGM' :
                raise Exception('Please use segmented frequency sweep')

            # check if the RF power is the same on both ports and for all
            # frequency segments
            count = int(vna.query(':SENS:FSEGM:COUN?'))
            vna_pow = None
            for i in range(1,count+1) :
                port1pow = float(vna.query(':SENS:FSEGM{}:POW:PORT1?'.format(i)))
                port2pow = float(vna.query(':SENS:FSEGM{}:POW:PORT2?'.format(i)))
                if vna_pow is None and port1pow == port2pow :
                    vna_pow = port1pow
                elif vna_pow is not None and port1pow == port2pow and port1pow == vna_pow :
                    continue
                else :
                    raise Exception("Please select the same power for all ports and frequency segments")
            port1att = vna.get_source_att(1)
            port2att = vna.get_source_att(2)
            if port1att == port2att :
                vna_pow -= port1att
            else:
                raise Exception("Please select the same attenuators for both ports")
            
            print("📻 ANRITSU VNA is set up.")
            print("----------------------------------------")
        except Exception as exc :
            print("⛔ There has been an error setting up the ANRITSU VNA.")
            raise exc
    measurement.vna = vna
    return vna, vna_pow



def initialise_oscillo(measurement=None) :
    return None
    # Connexion to the oscilloscope
    rm = pyvisa.ResourceManager()
    scope = rm.open_resource(adress.dpo71604c)
    if measurement is not None :
        measurement.scope = scope
    return scope


def initialise_lockin(measurement=None) :
    return None
    try :
        print("Setting up lock-in amplifier...")
        rm=visa.ResourceManager()
        lockin = rm.open_resource(adress.lockin_langevin)
        lockin.read_termination='\n\00'
        lockin.write_termination='\n\00'
        print("Lock-in is set up")
        print("----------------------------------------")
    except Exception as exc :
        print("⛔ There has been an error setting up lock-in amplifier.")
        raise exc
    if measurement is not None :
        measurement.lockin = lockin
    return lockin
