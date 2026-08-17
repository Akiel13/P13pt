"""
This module aims to provide a base class for instrument interfaces via pyvisa.
That class can then be inherited from in various instruments' divers.
"""

from __future__ import print_function
from typing import Text

try :
    from P13pt.mascril.progressbar import wait
except ImportError :
    import time
    wait = time.sleep

try :
    import pyvisa
except ImportError :
    import visa as pyvisa



def _print_resource(resource_manager, resource_name) :
    """
    Displays the name of the instrument.

    Parameters
    ----------
    resource_manager : pyvisa.ResourceManager
        Resource manager.
    resource_name : str
        Name of the instrument.

    Returns
    -------
    None.
    """
    try :
        instrument = resource_manager.open_resource(resource_name)
    except :
        print(f"{resource_name} -> connexion failure")
        return None
    try :
        print(f"{resource_name} -> '{instrument.query('ID?').strip()}'")
    except :
        print(f"{resource_name} -> '{instrument.query('*IDN?').strip()}'")
    instrument.close()
_print_resource.__annotations__ = {'resource_manager':pyvisa.ResourceManager,
                                   'resource_name':Text,
                                   'return':None}

def list_resources() :
    """
    Displays all instruments, and returns the list of their names.

    Returns
    -------
    resources_list : list[Text]
        List of the names of detected instruments.

    """
    rm = pyvisa.ResourceManager()
    resources_list = []
    for resource in rm.list_resources() :
        if not resource.startswith("ASRL") :
            _print_resource(rm, resource)
            resources_list.append(resource)
        else :
            print(resource)
    return resources_list


class PyvisaInstrument :
    """
    Python object meant to represent the connexion with an instrument.
    Subclasses should have a model attribute, that is the few first characters
    of the machine's response to a query asking for ID.
    """
    
    model : Text
    
    def __init__(self, adress=None) :
        
        self.adress = adress
        if adress == None :
            self.instrument = None
            print(f"UserWarning : {self} is not connected to any instrument")
            return None
        
        # set up connection
        self.rm = pyvisa.ResourceManager()
        self.instrument = self.rm.open_resource(adress)
        self.instrument.write_termination = '\n'
        self.instrument.read_termination = '\n'
        #self.instrument.clear() # Useful but should not be done all the time ?
        
        identifier = self.get_identifier()
        if not identifier.startswith(self.model) :
            nickname = repr(self).split(' object')[0]
            if len(repr(self).split(' object')) > 0 :
                nickname += repr(self)[-1]
            error_message = f"{nickname}.get_identifier() returned "
            error_message += f"{repr(identifier)}, expected {repr(self.model)}"
            raise WrongInstrumentError(error_message)
        
        

    # just wrapping the main functions of self.instrument
    def query(self, q):
        return self.instrument.query(q)
    
    # just wrapping the main functions of self.instrument
    def ask(self, q):
        return self.instrument.ask(q)
    
    # just wrapping the main functions of self.instrument
    def write(self, q):
        return self.instrument.write(q)
    
    # just wrapping the main functions of self.instrument
    def read(self) :
        return self.instrument.read()
    
    
    def get_identifier(self) :
        """
        Asks the machine for its identifier.
        """
        return self.query("*IDN")
    
    def _set_timeout(self, value) :
        self.instrument.timeout = value
    timeout = property(lambda self : self.instrument.timeout, _set_timeout)
    
    def _set_write_termination(self, value:str) :
        self.instrument.write_termination = value
    write_termination = property(
        lambda self : self.instrument.write_termination,
        _set_write_termination)
    
    def _set_read_termination(self, value:str) :
        self.instrument.read_termination = value
    read_termination = property(
        lambda self : self.instrument.read_termination, 
        _set_read_termination)
    
    
    def __del__(self) :
        self.instrument.close()




class WrongInstrumentError(Exception) :
    """
    The wrong instrument is connected.
    A connection was successfuly established, and the instrument responded
    to a request to identify itself, but the ID recieved was wrong.
    Probably the instrument at the given VISA identifier is not the one
    you wanted.    
    """
    pass
