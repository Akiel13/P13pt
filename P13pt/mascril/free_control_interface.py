import numpy as np
import tkinter as tk
from math import floor, ceil
from P13pt.mascril.waiting import wait
from P13pt.utils.plotting import si_prefixes
from P13pt.utils.file_management import string_to_float as interpret_string





def disable_widget(widget) :
    try :
        widget.config(state=tk.DISABLED)
    except :
        pass
    for child in widget.winfo_children() :
        disable_widget(child)

def enable_widget(widget):
    try :
        widget.config(state=tk.NORMAL)
    except :
        pass
    for child in widget.winfo_children() :
        enable_widget(child)

def widget_pauser(function, widget, delay=20) :
    def delayed_function(*args, **kwargs) :
        returned_values = function(*args, **kwargs)
        enable_widget(widget)
        return returned_values
    def decorated_function(*args, **kwargs) :
        disable_widget(widget)
        returned_values = widget.after(delay, lambda : delayed_function(*args, **kwargs))
        return returned_values
    return decorated_function





class ControlParameter :
    
    _update_value : callable
    var_name : str
    
    def __init__(self, var_name, update_function=None, factor=1):
        self.var_name = var_name
        self._update_value = update_function
        self.factor = factor
        
        if update_function is None :
            self._update_value = lambda *args, **kwargs : None
    
    
    def update(self, string, nonlocal_variables) :
        try :
            value = interpret_string(string) * self.factor
        except ValueError :
            print(f"Invalid numeral input : '{string}'")
            value = None
        except TypeError :
            value = None
        if value is None :
            return False
        self._update_value(value)
        nonlocal_variables[self.var_name] = value
        # Stabilise
        wait(nonlocal_variables["stabilisation_duration"])
        nonlocal_variables["measure_everything"](nonlocal_variables)
        return True





def free_control_sweep(nonlocal_variables, control_order, control_parameter_information) :

    popup = tk.Tk()
    popup.title("MAScriL aquisition control panel")
    controls_zone = tk.Frame(popup)
    controls_zone.pack()
    
    number_of_columns = ceil(np.sqrt(len(control_order)))
    
    control_parameter_units = control_parameter_information[0]
    control_parameter_order_of_magnitude = control_parameter_information[1]
    control_parameter_update_functions = control_parameter_information[2]
    
    def make_confirmation(function) :
        def decorated_function(*args, **kwargs) :
            returned_values = function(*args, **kwargs)
            confirmation_window = tk.Toplevel(popup)
            confirmation_window.title("MAScriL free control - ok")
            tk.Label(confirmation_window, text="value updated").pack()
            confirmation_window.after(370, confirmation_window.destroy)
            confirmation_window.mainloop()
            return returned_values
        return decorated_function
        
    
    for index, parameter in enumerate(control_order) :
        if parameter is None :
            continue
        multiplicative_factor = control_parameter_order_of_magnitude[parameter] * control_parameter_units[parameter][1]
        relevant_parameter = ControlParameter(parameter,
                      control_parameter_update_functions[parameter],
                      factor=multiplicative_factor)
        dedicated_zone = tk.Frame(controls_zone, borderwidth=2,
                                  relief="groove", padx=15, pady=10)
        dedicated_zone.grid(column=index % number_of_columns,
                            row=index // number_of_columns)
        tk.Label(dedicated_zone, text=f"{parameter} :").grid(column=0, row=0, columnspan=2)
        exponent = np.log10(control_parameter_order_of_magnitude[parameter])
        if exponent == floor(exponent) and floor(exponent) in si_prefixes.keys() :
            unit = si_prefixes[floor(exponent)] + control_parameter_units[parameter][0]
        else :
            unit = f"×{control_parameter_order_of_magnitude[parameter]} {control_parameter_units[parameter][0]}"
        tk.Label(dedicated_zone, text=unit, pady=5).grid(column=1, row=1)
        value_field = tk.Entry(dedicated_zone)
        value_field.grid(column=0, row=1)
        button_command = widget_pauser(lambda x=relevant_parameter, y=value_field : x.update(y.get(), nonlocal_variables), controls_zone)
        confirm_button = tk.Button(dedicated_zone, text="Confirm", command=make_confirmation(button_command))
        confirm_button.grid(column=0, row=2, columnspan=2)
    
    label = tk.Label(popup, text="\nMeasurement will end when this window is closed.")
    label.pack()
    popup.mainloop()