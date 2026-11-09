# -*- coding: utf-8 -*-
"""
Register of adresses of machines in P13
"""


# ✨ Adresses ✨


# Refer to the following link to learn more to communicate with instruments using pyvisa:
# https://pyvisa.readthedocs.io/en/latest/introduction/communication.html




# Keithley voltage sources
k2400 = {'Cascade':'GPIB::24::INSTR',
         'JANIS':'GPIB::24::INSTR',}
k2400_2 = {'Cascade':'GPIB::2::INSTR',}
k2612 = {'Christian':'GPIB::26::INSTR',
         'Raman':'USB0::0x05E6::0x2612::4469735::0::INSTR'}

# Other voltage sources
yoko = {'Cascade':'GPIB::6::INSTR',
        'JANIS':'GPIB::3::INSTR',}

# Temperature controller
tic500 = {'Cascade':'ASRL4::INSTR',} # The TIC500 address depends on which port the USB cable is physically plugged

# VNA
zva67 = {'Cascade':'GPIB::20::INSTR',}

# Oscilloscope
dpo71604c = {'Cascade':'GPIB::1::INSTR',} # Oscilloscope

# Lock-in
dsp7270 = {'Langevin':'USB0::0x0A2D::0x001B::09295884::RAW'}





# 🧓🏾 Old machines we don't use anymore
# ⚠ Those adresses are probably outdated
anritsu = {'JANIS':'GPIB::6::INSTR',}
k2600 = {'JANIS':'GPIB::24::INSTR',}
k2000 = {'Cascade':'GPIB::15::INSTR',
         'JANIS':'GPIB::20::INSTR',}
si9700 = {'JANIS':'GPIB::14::INSTR',}



# 😒 Whatever was going on with the BILT
bilt = {'Cascade':'TCPIP0::192.168.0.5::5025::SOCKET',
        'JANIS':'TCPIP0::192.168.0.2::5025::SOCKET',}
position_source_bilt = {'Cascade':'I3;C',
                        'JANIS':'I',}
position_meter_bilt = {'Cascade':'I1;C',
                       'JANIS':'I5;C',}