# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 19:26:34 2019

@author: Aurélien Schmitt
"""
"""
Driver for the Agilent 8114a pulse generator

for PyVISA 1.8

contains elements from an acquisition script written by Holger Graef and Romaric Le Goff
"""

from P13pt.drivers.base import PyvisaInstrument, WrongInstrumentError

class Agi8114a(PyvisaInstrument) :
    
    model = 'HEWLETT-PACKARD,HP8114A'
    agi8114a = property(lambda self : self.instrument)
    
    def __init__(self, connection, sourcemode='V', vrang=None, irang=None,
                 initialise=True):
        self.time_step = 0.01     # update voltage every 10 ms when sloping
        
        # set up connection
        super(Agi8114a, self).__init__(connection)      
        self.agi8114a.clear()
               
        if not self.query('*IDN?').startswith('HEWLETT-PACKARD,HP8114A,DE38601455,REV 01.15.00'):
            raise WrongInstrumentError('Instrument not compatible with Agilent 8114a driver')

        if initialise:        
            self.write(":STATus:QUEue:CLEar")
            self.write(":OUTPut OFF")
           
            if sourcemode.lower() == 'v':
                #self.sourcemode = 'v'
                
                #self.write(':SOUR:FUNC VOLT')
                self.write(':OUTP:POL POS')
                self.write(':SOUR:VOLT 1')
                #self.write(':SOUR:VOLT:BAS 0')
                self.write(':SOUR:FREQ 10')
            elif sourcemode.lower() == 'i':
                #self.sourcemode = 'i'
                self.write(':SOUR:HOLD CURR')
                self.write(':OUTP:POL POS')
                self.write(':SOUR:CURR 1')
                #self.write(':SOUR:CURR:BAS 0')
                self.write(':SOUR:FREQ 10')

            if vrang is not None:
                self.write(":SOURce:VOLTage:RANGe "+str(vrang))
            if irang is not None:
                self.write(":SOURce:CURR:RANGe "+str(irang))
            
            self.write(":OUTP ON")

        '''if not self.query('SYST:ERR?').startswith('0,'):
            raise Exception("Agilent 8114a signals error")'''
    

    
#    def set_voltage(self, amplitude, frequency):
#        #if not self.query(':SOUR:FUNC:MODE?') == 'VOLT':
#        #    raise Exception('The instrument is not set as voltage source')
#        #if (offset+amplitude/2) > float(self.query(':SOUR:VOLT:RANG?')):
#        #    raise Exception('The requested voltage is out of range')
#            
#        #set voltage limits not to kill the device
#        self.write(":SOUR:VOLT:LIM 10")
#        self.write(":SOUR:VOLT:LIM:STAT ON")
#        
#        #set duty cycle and keep it constant
#        self.write(":SOUR:PULS:DCYC 70")
#        self.write(":SOUR:PULS:HOLD DCYC")
#        
##        # set offset voltage
##        off_init=self.query(':SOUR:VOLT:BAS?')
##        time_step = self.time_step
##        v_step = time_step*self.slope
##        if np.abs(offset-off_init) < v_step:
##            self.write(":SOUR:VOLT:BAS "+str(offset))
##            return 
##        slow_list = np.arange(off_init, offset,
##                              np.sign(offset-off_init)*v_step)
##        for i in slow_list:
##            sleep(time_step)
##            self.write(":SOUR:VOLT:BAS "+str(i))
##        self.write(":SOUR:VOLT:BAS "+str(offset))
#        
#        #set amplitude
#        amp_init=self.query(':SOUR:VOLT?')
#        time_step = self.time_step
#        v_step = time_step*self.slope
#        if np.abs(amplitude-float(amp_init)) < v_step:
#            self.write(":SOUR:VOLT "+str(amplitude))
#            return 
#        slow_list = np.arange(amp_init, amplitude,
#                              np.sign(amplitude-float(amp_init))*v_step)
#        for i in slow_list:
#            sleep(time_step)
#            self.write(":SOUR:VOLT "+str(i))
#        self.write(":SOUR:VOLT "+str(amplitude))
#        #set pulse frequency
#        self.write(":SOUR:FREQ "+str(frequency))
        

    def set_voltage(self, amplitude, frequency):
        #if not self.query(':SOUR:FUNC:MODE?') == 'VOLT':
        #    raise Exception('The instrument is not set as voltage source')
        #if (offset+amplitude/2) > float(self.query(':SOUR:VOLT:RANG?')):
        #    raise Exception('The requested voltage is out of range')
            
        #set voltage limits not to kill the device
        self.write(":SOUR:VOLT:LIM 10")
        #self.write(":SOUR:VOLT:LIM:STAT ON")
        
        #set duty cycle and keep it constant
        self.write(":SOUR:PULS:DCYC 50")
        #self.write(":SOUR:PULS:HOLD DCYC")
        
#        # set offset voltage
#        off_init=self.query(':SOUR:VOLT:BAS?')
#        time_step = self.time_step
#        v_step = time_step*self.slope
#        if np.abs(offset-off_init) < v_step:
#            self.write(":SOUR:VOLT:BAS "+str(offset))
#            return 
#        slow_list = np.arange(off_init, offset,
#                              np.sign(offset-off_init)*v_step)
#        for i in slow_list:
#            sleep(time_step)
#            self.write(":SOUR:VOLT:BAS "+str(i))
#        self.write(":SOUR:VOLT:BAS "+str(offset))
        
        #set amplitude
        amp_init=self.query(':SOUR:VOLT?')
        self.write(":SOUR:VOLT "+str(amplitude))
        #set pulse frequency
        self.write(":SOUR:FREQ "+str(frequency))

        
    def get_currsetpoint(self):
        return float(self.query(':SOUR:CURR?'))
    
    def get_voltsetpoint(self):
        return float(self.query(':SOUR:VOLT?'))
        
    def get_voltage(self):
        self.query(':SENS:FUNC:OFF "CURR:DC"')
        self.query(':SENS:FUNC:ON "VOLT:DC"')
        return float(self.query(':read?').split(',')[0])
        
    def get_current(self):
        self.query(':SENS:FUNC:OFF "VOLT:DC"')
        self.query(':SENS:FUNC:ON "CURR:DC"')
        return float(self.query(':read?').split(',')[1])


if __name__ == '__main__':
    agi8114a = Agi8114a('GPIB::26::INSTR')
