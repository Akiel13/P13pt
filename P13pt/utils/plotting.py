from __future__ import print_function

import os
import numpy as np

from math import floor

from matplotlib.ticker import FuncFormatter
from P13pt.utils.colors import plt
from P13pt.utils.file_management import preserve_cwd, generate_archiving_function

plt.rcParams['figure.max_open_warning'] = 70


def magnitude(array, puissance=1) :
    try :
        subarray = array[np.invert(np.isnan(array))]
    except TypeError :
        subarray=np.array([array]).astype(float)
    if len(subarray) == 0 :
        return 0
    avg = np.average(np.abs(subarray)**2)
    if avg == 0 :
        return 0
    exponent = floor(np.log10(avg)/puissance/2)
    if puissance != 1 and exponent in [-2, -1, 1, 2] :
        return exponent
    if exponent in [-1,3] :
        exponent = 1
    return 3 * (exponent//3)


def engineer_str(x, latex=False) :
    """Semi-scientific notation"""
    exponent_characters = {"0":"⁰", "1":"¹", "2":"²", "3":"³", "4":"⁴",
                           "5":"⁵", "6":"⁶", "7":"⁷", "8":"⁸", "9":"⁹",
                           "-":"⁻"}
    exponent = magnitude(x)
    mantisse = x * 10**(-exponent)
    returned_string = f"{mantisse:.12f}".replace("000000","!")
    returned_string = returned_string.split("!")[0]
    if returned_string[-1] == "." :
        returned_string += "0"
    if exponent == 0 :
        return returned_string
    returned_string += "×10"
    if latex :
        returned_string += "$^{"+str(exponent)+"}$"
        return returned_string
    for char in str(exponent) :
        returned_string += exponent_characters[char]
    return returned_string

engineer_formatter = FuncFormatter(lambda x, pos : engineer_str(x, latex=True))
si_prefixes = {-30:"q",-27:"r",-24:"y",-21:"z",-18:"a",-15:"f",-12:"p",-9:"n",
               -6:"µ",  -3:"m", -2:"c", -1:"d",  0:"",   1:"da", 2:"h", 3:"k",
                6:"M",   9:"G", 12:"T", 15:"P", 18:"E", 21:"Z", 24:"Y", 27:"R",
               30:"Q"}

def si_prefix(array, puissance=1) :
    return si_prefixes[magnitude(array, puissance)]

def scale(array, puissance=1) :
    exponent = magnitude(array, puissance)
    return 10**-(exponent*puissance), si_prefixes[exponent]

def preplot(*args) :
    liste = []
    for array in args :
        a, b = scale(array)
        liste.append(a)
        liste.append(b)
    return liste

def scaled_plot(*args, xscale=None, yscale=None, autoscale=False, graph=None, **kwargs) :
    if xscale == None and not autoscale :
        xscale = 1
    if yscale == None and not autoscale :
        yscale = 1
    if xscale == 1 and yscale == 1 :
        if graph is None :
            return plt.plot(*args, **kwargs)
        return graph.plot(*args, **kwargs)
    p = ""
    k = 0
    for a in args :
        if type(a) == str :
            p = p[:-1] + "y_"
            k = 0
        else :
            p = p + "xy"[k]
            k = 1 - k
    if len(p) != len(args) :
        print("problèmes")
    li = []
    for j,a in enumerate(args) :
        if xscale == None and p[j] == "x" :
            xscale = scale(a)[0]
        if yscale == None and p[j] == "y" :
            yscale = scale(a)[0]
        if p[j] == "_" :
            li.append(a)
        elif p[j] == "x" :
            li.append(np.array(a)*xscale)
        elif p[j] == "y" :
            li.append(np.array(a)*yscale)
    if graph is None :
        return plt.plot(*li, **kwargs)
    return graph.plot(*li, **kwargs)


def make_grid(graph=None, **kwargs) :
    if graph is None :
        xlims = plt.xlim()
        ylims = plt.ylim()
        plt.xlim(*xlims)
        plt.ylim(*ylims)
        axes = plt
    else :
        xlims = graph.get_xlim()
        ylims = graph.get_ylim()
        graph.set_xlim(*xlims)
        graph.set_ylim(*ylims)
        axes = graph
    axes.grid(**kwargs)
    axes.hlines(0, *xlims, "k", lw=1, zorder=1.7)
    axes.vlines(0, *ylims, "k", lw=1, zorder=1.7)








def generate_figure_save_function(work_directory, results_archive) :
    @preserve_cwd
    def save_figure(title) :
        os.chdir(work_directory)
        archive_file = generate_archiving_function(work_directory, results_archive)
        if "." in title :
            plt.savefig(title)
            archive_file(title)
        else :
            plt.savefig(f"{title}.svg")
            archive_file(f"{title}.svg")
            plt.savefig(f"{title}.png")
            archive_file(f"{title}.png")
        print("")
    return save_figure
    
    








def figures_generator(filename="") :


    def figure(*args, width=None, aspect_ratio=13/16, figsize=None, constrained_layout=True, overtitle=None, height=None, **kwargs) :
        if width is None and height is None :
            width = 6
        elif width is None :
            width = height / aspect_ratio
        if figsize is None :
            figsize = (width, width*aspect_ratio)
        if figsize[0] > 2**8 : figsize = (2**8, *figsize[1:])
        if figsize[1] > 2**8 : figsize = (figsize[0], 2**8, *figsize[2,:])
        fig = plt.figure(*args, figsize=figsize, constrained_layout=constrained_layout, **kwargs)
        if overtitle is None :
            try :
                overtitle = filename
            except NameError :
                overtitle = ""
        fig.suptitle(overtitle, size=6)
        return fig
    
    def smallfigure(*args, dpi=70, **kwargs) :
        return figure(*args, dpi=dpi, **kwargs)
    
    def bigfigure(*args, dpi=170, **kwargs) :
        return figure(*args, dpi=dpi, **kwargs)
    
    def hugefigure(*args, dpi=255, **kwargs) :
        return figure(*args, dpi=dpi, **kwargs)
    
    return figure, smallfigure, bigfigure, hugefigure

figure, smallfigure, bigfigure, hugefigure = figures_generator()