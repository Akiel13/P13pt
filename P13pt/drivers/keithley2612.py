"""
Driver for the Keithley 2612 SourceMeter

for PyVISA 1.8

@author: Holger Graef

contains elements from an acquisition script written by Romaric Le Goff
"""


import numpy as np
from P13pt.drivers.base import PyvisaInstrument, WrongInstrumentError, wait





class K2612(PyvisaInstrument) :
    
    model = '2612'
    k2612 = property(lambda self : self.instrument)
    
    
    def __init__(self, connection, channel='A', slope=0.01, initialise=True, reset=True):
        # TODO: check for error at end of init
        # TODO: implement range setting
        
        super(K2612, self).__init__(connection)
        
        self.slope = slope
        self.time_step = 0.01     # update voltage every 10 ms when sloping
        self.channel = channel.lower()
        if self.channel not in ['a', 'b']:
            raise Exception('Invalid channel')
        
        if reset:
            self.k2612.clear()   # if a different channel was set up previously and we execute this, the other channel is switched off
        
        if not self.query('print(localnode.model)').startswith('261'):
            raise WrongInstrumentError('Instrument not compatible with Keithley 2612 driver')
            
        if initialise:
            if reset:
                self.write("reset()")
            self.write("display.smu"+self.channel+".measure.func = display.MEASURE_DCAMPS")
            
            self.write("smu"+self.channel+".source.func = smu"+self.channel+".OUTPUT_DCVOLTS")
            self.write("smu"+self.channel+".source.output = smu"+self.channel+".OUTPUT_ON")
        
    def set_voltage(self, value):
        # set voltage
        time_step = self.time_step
        v_step = time_step*self.slope
        
        current_volt = self.get_voltsetpoint()
        if np.abs(value-current_volt) <= v_step :
            self.write(f'smu{self.channel}.source.levelv = {value}')
            return 
        slow_list = np.arange(current_volt, value, np.sign(value-current_volt)*v_step)
        for volt in slow_list:
            wait(time_step)
            self.write(f'smu{self.channel}.source.levelv = {volt}')
        self.write(f'smu{self.channel}.source.levelv = {value}')
        
    def set_current(self, value):
        # set voltage
        time_step = self.time_step
        i_step = time_step*self.slope
        
        current_amp = self.get_ampsetpoint()
        if np.abs(value-current_amp)<=i_step:
            self.write('smu'+self.channel+'.source.leveli = '+str(value))
            return 
        slow_list = np.arange(current_amp, value, np.sign(value-current_amp)*i_step)
        for amp in slow_list:
            wait(time_step)
            self.write('smu'+self.channel+'.source.leveli = '+str(amp))
        self.write('smu'+self.channel+'.source.leveli = '+str(value))
       
    def get_voltsetpoint(self):
        return float(self.query('print(smu'+self.channel+'.source.levelv)'))
        
    def get_ampsetpoint(self):
        return float(self.query('print(smu'+self.channel+'.source.leveli)'))
        
    def get_voltage(self):
        return float(self.query('print(smu'+self.channel+'.measure.v())'))
        
    def get_current(self):
        return float(self.query('print(smu'+self.channel+'.measure.i())'))


    def get_identifier(self) :
        return self.query('print(localnode.model)')


















if __name__ == '__main__':
    k2612 = K2612('GPIB::26::INSTR')