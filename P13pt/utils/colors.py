# -*- coding: utf-8 -*-
"""
Created on Mon Jun 15 10:20:05 2026

@author: Vincent
"""


import numpy as np
import matplotlib.pyplot as plt
from collections.abc import Callable
π = np.pi
import copy
from typing import List








def softmax(array) :
    """Returns the maximum of an array, without using comparisons.
    The algorith uses mathematical operations between the elements of array : addition, substraction, absolute value, multiplication by a scalar.
    It is quite inefficient at actually finding the maximum of a long iterable.
    The intended use case is to compare a numpy.array with a float, in which case you get an element-wise maximum
    
    Example : 
    In [1]: softmax([3, np.arange(7)])
    Out [1]: array([3., 3., 3., 3., 4., 5., 6.])
    """
    if np.isscalar(array) :
        return array
    current_maximum = array[0]
    unprocessed_elements = [x for x in array[1:]]
    while len(unprocessed_elements) > 0 :
        new_element = unprocessed_elements.pop()
        current_maximum = .5 * (current_maximum + np.abs(new_element-current_maximum) + new_element)
    return current_maximum

def softmin(array) :
    """Returns the minimum of an array, without using comparisons.
    The algorith uses mathematical operations between the elements of array : addition, substraction, absolute value, multiplication by a scalar.
    It is quite inefficient at actually finding the minimum of a long iterable.
    The intended use case is to compare a numpy.array with a float, in which case you get an element-wise minimum
    
    Example : 
    In [1]: softmin([3, np.arange(7)])
    Out [1]: array([0., 1., 2., 3., 3., 3., 3.])
    """
    if np.isscalar(array) :
        return array
    current_minimum = array[0]
    unprocessed_elements = [x for x in array[1:]]
    while len(unprocessed_elements) > 0 :
        new_element = unprocessed_elements.pop()
        current_minimum = .5 * (current_minimum - np.abs(new_element-current_minimum) + new_element)
    return current_minimum






























def lagrange_polynomial(*tuples:List[tuple]) -> Callable :
    
    def deep_deep(depth, liste) :
        if depth == 0 :
            return 1
        total = 0
        for m in range(depth-1,len(liste)) :
            total -= liste[m] * deep_deep(depth-1, liste[:m])
        return total
    
    degre = len(tuples)
    
    x_list = np.array([tup[0] for tup in tuples])
    y_list = np.array([tup[1] for tup in tuples])
    
    matrix = np.matmul(np.ones((degre,1)),np.array([x_list]))
    difference_matrix = matrix.transpose() - matrix
    
    lignes = np.diag(1/difference_matrix.prod(axis=1, where=(np.ones((degre,degre))!=np.eye(degre))))
    
    colonnes = np.array([[deep_deep(degre-1-d, x_list[np.arange(degre)!=m]) for m in range(degre)] for d in range(degre)])
    
    coeffs = np.matmul(np.matmul(colonnes, lignes),y_list)
    P = lambda x : np.matmul(coeffs,np.array([x**k for k in range(degre)]))
    return P

































class ColorConverter :
    
    ### sRGB representation :
    # 3 numbers between 0 and 255
    # sRGB "White" is 255 | 255 | 255
    
    def sRGB_to_hex(self, R, G, B) :
        """Note : if your version of numpy is too recent, your np.char might have been renamed 'np.strings' : it works similarly"""
        if np.__version__.split(".")[0] == "1" :
            rjust = np.char.rjust
            lstrip = np.char.lstrip
            add_string = np.char.add
        else :
            rjust = np.strings.rjust
            lstrip = np.strings.lstrip
            add_string = np.strings.add
        
        if not np.isscalar(R) :
            rgb_string = np.empty(np.shape(R), dtype = "<U1")
            rgb_string[:] = "#"
        elif not np.isscalar(G) :
            rgb_string = np.empty(np.shape(G), dtype = "<U1")
            rgb_string[:] = "#"
        elif not np.isscalar(B) :
            rgb_string = np.empty(np.shape(B), dtype = "<U1")
            rgb_string[:] = "#"
        else :
            rgb_string = "#"
        for i in range(3) :
            X = (R, G, B)[i]
            T = softmin([softmax([0,np.divmod(X,1)[0]]),255]).astype(int)
            if np.isscalar(T) :
                hx = hex(T)
                hx = hx.lstrip("0")
                hx = hx.lstrip("x")
                hx = hx.rjust(2, "0")
            else :
                hx = np.vectorize(hex)(T)
                hx = lstrip(hx, "0")
                hx = lstrip(hx, "x")
                hx = rjust(hx, 2, "0")
            rgb_string = add_string(rgb_string, hx)
            #print(rgb_string)
        if (np.shape(rgb_string) == ()) and R <= 255 and G <= 255 and B <= 255 :
            rgb_string = str(rgb_string)
        elif (np.shape(rgb_string) == ()) :
            rgb_string = "#888888"
            print("1 sRGB saturation")
        else :
            overflow_mask = (R > 255)|(G > 255)|(B > 255)
            if True in overflow_mask :
                #rgb_string = rgb_string.astype("<U9")
                print(f"{sum(overflow_mask)} sRGB saturations")
                rgb_string[overflow_mask] = "#888888"
        return rgb_string
        
    def sRGB_to_hex_unbound(self, R, G, B) :
        r = softmin([R, 255])
        g = softmin([G, 255])
        b = softmin([B, 255])
        return self.sRGB_to_hex(r, g, b)
    
    def hex_to_sRGB(self, string) :
        if np.__version__.split(".")[0] == "1" :
            lstrip = np.char.lstrip
        else :
            lstrip = np.strings.lstrip

        if np.shape(string) == () :
            hx = string.lstrip("0x")
            hx = hx.lstrip("x")
            hx = hx.lstrip("#")
            R = int(hx[0:2],16)
            G = int(hx[2:4],16)
            B = int(hx[4:6],16)
        else :
            hx = lstrip(string,"0x")
            hx = lstrip(hx,"x")
            hx = lstrip(hx,"#")
            RGB = np.vectorize(int)(hx,16)
            RG,B = np.divmod(RGB,256)
            R, G = np.divmod(RG,256)
        return R, G, B
    
    
    
    ### CIE XYZ
    # 3 numbers between 0 & ~100
    # sRGB "White" is 95.05 | 93.5 | 108.9
    
    matrix_sRGB_to_CIEXYZ = np.array([[0.4124,0.3576,0.1805], [0.2126,0.7152,0.00722], [0.0193,0.1192,0.9505]])
    matrix_CIEXYZ_to_sRGB = np.linalg.inv(matrix_sRGB_to_CIEXYZ)
    γ_CIEXYZ_to_sRGB = 0.04045 / 12.92
    
    def CIEXYZ_to_sRGB(self, X, Y, Z) :
        γ = self.γ_CIEXYZ_to_sRGB
        def EsRGB(v) :
            result = np.zeros(np.shape(v))
            result[v <= γ] = np.array(v)[v <= γ] * 12.92
            result[v > γ] = 1.055 * np.array(v)[v > γ]**(5/12) - 0.055
            return result
        xyz = np.array([X, Y, Z]) / 100
        RGB_primary = np.matmul(self.matrix_CIEXYZ_to_sRGB, xyz)
        R, G, B = 255*EsRGB(RGB_primary)
        return R, G, B

    def sRGB_to_CIEXYZ(self, R, G, B) :
        def DsRBG(u) :
            result = np.zeros(np.shape(u))
            result[u <= 0.04045] = np.array(u)[u <= 0.04045] / 12.92
            result[u > 0.04045] = ((np.array(u)[u > 0.04045] + 0.055)/1.055)**2.4
            return result
        RGB_primary = DsRBG(np.array([R, G, B])/255)
        X, Y, Z = np.matmul(self.matrix_sRGB_to_CIEXYZ, RGB_primary) * 100
        return X, Y, Z
    
    def CIEXYZ_to_hex(self, X, Y, Z) :
        return self.sRGB_to_hex(*self.CIEXYZ_to_sRGB(X, Y, Z))
    
    def hex_to_CIEXYZ(self, string) :
        return self.sRGB_to_CIEXYZ(*self.hex_to_sRGB(string))
    
    
    
    ### OkLab
    
    matrix_CIEXYZ_to_lms = np.array([[0.8189330101,0.3618667424,-0.1288597137], [0.0329845436,0.9293118715,0.0361456387], [0.0482003018,0.2643662691,0.6338517070]])
    matrix_lms_to_OkLab = np.array([[0.2104542553,0.7936177850,-0.0040720468], [1.9779984951,-2.4285922050,0.4505937099], [0.0259040371,0.7827717662,-0.8086757660]])
    matrix_lms_to_CIEXYZ = np.linalg.inv(matrix_CIEXYZ_to_lms)
    matrix_OkLab_to_lms = np.linalg.inv(matrix_lms_to_OkLab)
    
    def CIEXYZ_to_OkLab(self, X, Y, Z) :
        XYZ = np.array([X, Y, Z])/100
        lms = np.matmul(self.matrix_CIEXYZ_to_lms, XYZ)
        L, a, b = np.matmul(self.matrix_lms_to_OkLab, lms**(1/3))
        return L, a, b

    def OkLab_to_CIEXYZ(self, L, a, b) :
        if np.isscalar(b) and not np.isscalar(L) :
            b = np.full(np.shape(L), b)
        if np.isscalar(L) and not np.isscalar(a) :
            L = np.full(np.shape(a), L)
        if np.isscalar(a) and not np.isscalar(b) :
            a = np.full(np.shape(b), a)
        if np.isscalar(b) and not np.isscalar(L) :
            b = np.full(np.shape(L), b)
        Lab = np.array([L, a, b])
        lms = np.matmul(self.matrix_OkLab_to_lms, Lab)**3
        X, Y, Z = np.matmul(self.matrix_lms_to_CIEXYZ, lms)*100
        return X, Y, Z
    
    def OkLab_to_sRGB(self, L, a, b) :
        return self.CIEXYZ_to_sRGB(*self.OkLab_to_CIEXYZ(L, a, b))

    def sRGB_to_OkLab(self, R, G, B) :
        return self.CIEXYZ_to_OkLab(*self.sRGB_to_CIEXYZ(R, G, B))
    
    def OkLab_to_hex(self, L, a, b) :
        return self.CIEXYZ_to_hex(*self.OkLab_to_CIEXYZ(L, a, b))
    
    def hex_to_OkLab(self, string) :
        return self.CIEXYZ_to_OkLab(*self.hex_to_CIEXYZ(string))
    
    # Cylindrical coordinates version
    
    def OkLCh_to_OkLab(self, L, h, C) :
        a = C * np.cos(h)
        b = C * np.sin(h)
        return L, a, b

    def OkLab_to_OkLCh(self, L, a, b) :
        h = np.arctan2(b,a)
        C = np.sqrt(a*a + b*b)
        return L, h, C
    
    def OkLCh_to_CIEXYZ(self, L, h, C) :
        return self.OkLab_to_CIEXYZ(*self.OkLCh_to_OkLab(L, h, C))
        
    def CIEXYZ_to_OkLCh(self, X, Y, Z) :
        return self.OkLab_to_OkLCh(*self.CIEXYZ_to_OkLab(X, Y, Z))
    
    def OkLCh_to_sRGB(self, L, h, C) :
        return self.CIEXYZ_to_sRGB(*self.OkLCh_to_CIEXYZ(L, h, C))

    def sRGB_to_OkLCh(self, R, G, B) :
        return self.CIEXYZ_to_OkLCh(*self.sRGB_to_CIEXYZ(R, G, B))
    
    def OkLCh_to_hex(self, L, h, C) :
        return self.CIEXYZ_to_hex(*self.OkLCh_to_CIEXYZ(L, h, C))
    
    def hex_to_OkLCh(self, string) :
        return self.CIEXYZ_to_OkLCh(*self.hex_to_CIEXYZ(string))
    
    
    
    ### CIELab
    
    δ_CIELab = (3/2) * (16/116)
    # Standard D65 : Xn = 95.0489 & Zn = 108.884
    Xn_standard_D65 = 95.0489
    Zn_standard_D65 = 108.884
    # Standard D50 : Xn = 96.4212 & Zn = 82.5188
    Xn_standard_D50 = 96.4212
    Zn_standard_D50 = 82.5188
    
    def CIELab_to_CIEXYZ(self, L, a, b) :
        def Cxyz(y) :
            result = np.zeros(np.shape(y))
            result[y > δ] = np.array(y)[y > δ]**3
            result[y <= δ] = (3*np.array(y)[y <= δ] - 2*δ)*δ*δ
            return result
        Xn = self.Xn_standard_D65
        Zn = self.Zn_standard_D65
        δ = self.δ_CIELab
        s = (L + 16) / 116
        X = Xn * Cxyz(s + a / 500)
        Y = 100 * Cxyz(s)
        Z = Zn * Cxyz(s - b / 200)
        return X, Y, Z

    def CIEXYZ_to_CIELab(self, X, Y, Z) :
        def gδ(t) :
            result = np.zeros(np.shape(t))
            result[t > δ**3] = np.array(t)[t > δ**3]**(1/3)
            result[t <= δ**3] = (np.array(t)[t <= δ**3]/δ/δ + 2*δ)/3
            return result
        Xn = self.Xn_standard_D65
        Zn = self.Zn_standard_D65
        δ = self.δ_CIELab
        t = gδ(Y/100)
        L = t * 116 - 16
        a = 500 * (gδ(X/Xn) - t)
        b = 200 * (t - gδ(Z/Zn))
        return L, a, b
    
    def CIELab_to_sRGB(self, L, a, b) :
        return self.CIEXYZ_to_sRGB(*self.CIELab_to_CIEXYZ(L, a, b))

    def sRGB_to_CIELab(self, R, G, B) :
        return self.CIEXYZ_to_CIELab(*self.sRGB_to_CIEXYZ(R, G, B))
    
    def CIELab_to_hex(self, L, a, b) :
        return self.CIEXYZ_to_hex(*self.CIELab_to_CIEXYZ(L, a, b))
    
    def hex_to_CIELab(self, string) :
        return self.CIEXYZ_to_CIELab(*self.hex_to_CIEXYZ(string))
    
    def CIELab_to_OkLab(self, L, a, b) :
        return self.CIEXYZ_to_OkLab(*self.CIELab_to_CIEXYZ(L, a, b))
    
    def OkLab_to_CIELab(self, L, a, b) :
        return self.CIEXYZ_to_CIELab(*self.OkLab_to_CIEXYZ(L, a, b))
    
    def CIELab_to_OkLCh(self, L, a, b) :
        return self.CIEXYZ_to_OkLCh(*self.CIELab_to_CIEXYZ(L, a, b))
    
    def OkLCh_to_CIELab(self, L, h, C) :
        return self.CIEXYZ_to_CIELab(*self.OkLCh_to_CIEXYZ(L, h, C))
    
    # Cylindrical coordinates version
    
    def CIELCh_to_CIELab(self, L, h, C) :
        a = C * np.cos(h)
        b = C * np.sin(h)
        return L, a, b

    def CIELab_to_CIELCh(self, L, a, b) :
        h = np.arctan2(b,a)
        C = np.sqrt(a*a + b*b)
        return L, h, C
    
    def CIELCh_to_CIEXYZ(self, L, h, C) :
        return self.CIELab_to_CIEXYZ(*self.CIELCh_to_CIELab(L, h, C))
        
    def CIEXYZ_to_CIELCh(self, X, Y, Z) :
        return self.CIELab_to_CIELCh(*self.CIEXYZ_to_CIELab(X, Y, Z))
    
    def CIELCh_to_sRGB(self, L, h, C) :
        return self.CIEXYZ_to_sRGB(*self.CIELCh_to_CIEXYZ(L, h, C))

    def sRGB_to_CIELCh(self, R, G, B) :
        return self.CIEXYZ_to_CIELCh(*self.sRGB_to_CIEXYZ(R, G, B))
    
    def CIELCh_to_hex(self, L, h, C) :
        return self.CIEXYZ_to_hex(*self.CIELCh_to_CIEXYZ(L, h, C))
    
    def hex_to_CIELCh(self, string) :
        return self.CIEXYZ_to_CIELCh(*self.hex_to_CIEXYZ(string))
    
    def CIELCh_to_OkLab(self, L, h, C) :
        return self.CIEXYZ_to_OkLab(*self.CIELCh_to_CIEXYZ(L, h, C))
    
    def OkLab_to_CIELCh(self, L, a, b) :
        return self.CIEXYZ_to_CIELCh(*self.OkLab_to_CIEXYZ(L, a, b))
    
    def CIELCh_to_OkLCh(self, L, h, C) :
        return self.CIEXYZ_to_OkLCh(*self.CIELCh_to_CIEXYZ(L, h, C))
    
    def OkLCh_to_CIELCh(self, L, h, C) :
        return self.CIEXYZ_to_CIELCh(*self.OkLCh_to_CIEXYZ(L, h, C))
    
    
    
    ### CIEYxy
    
    def CIEYxy_to_CIEXYZ(self, Y, x, y) :
        T = (Y/y) # X + Y + Z
        X = T * x
        Z = T - X - Y
        return X, Y, Z

    def CIEXYZ_to_CIEYxy(self, X, Y, Z) :
        T = X + Y + Z
        x = X / T
        y = Y / T
        return Y, x, y
    
    def CIEYxy_to_sRGB(self, Y, x, y) :
        return self.CIEXYZ_to_sRGB(*self.CIEYxy_to_CIEXYZ(Y, x, y))

    def sRGB_to_CIEYxy(self, R, G, B) :
        return self.CIEXYZ_to_CIEYxy(*self.sRGB_to_CIEXYZ(R, G, B))
    
    def CIEYxy_to_hex(self, Y, x, y) :
        return self.CIEXYZ_to_hex(*self.CIEYxy_to_CIEXYZ(Y, x, y))
    
    def hex_to_CIEYxy(self, string) :
        return self.CIEXYZ_to_CIEYxy(*self.hex_to_CIEXYZ(string))
    
    def CIEYxy_to_OkLab(self, Y, x, y) :
        return self.CIEXYZ_to_OkLab(*self.CIEYxy_to_CIEXYZ(Y, x, y))
    
    def OkLab_to_CIEYxy(self, L, a, b) :
        return self.CIEXYZ_to_CIEYxy(*self.OkLab_to_CIEXYZ(L, a, b))
    
    def CIEYxy_to_OkLCh(self, Y, x, y) :
        return self.CIEXYZ_to_OkLCh(*self.CIEYxy_to_CIEXYZ(Y, x, y))
    
    def OkLCh_to_CIEYxy(self, L, h, C) :
        return self.CIEXYZ_to_CIEYxy(*self.OkLCh_to_CIEXYZ(L, h, C))
    
    def CIEYxy_to_CIELab(self, Y, x, y) :
        return self.CIEXYZ_to_CIELab(*self.CIEYxy_to_CIEXYZ(Y, x, y))
    
    def CIELab_to_CIEYxy(self, L, a, b) :
        return self.CIEXYZ_to_CIEYxy(*self.CIELab_to_CIEXYZ(L, a, b))
    
    def CIEYxy_to_CIELCh(self, Y, x, y) :
        return self.CIEXYZ_to_CIELCh(*self.CIEYxy_to_CIEXYZ(Y, x, y))
    
    def CIELCh_to_CIEYxy(self, L, h, C) :
        return self.CIEXYZ_to_CIEYxy(*self.CIELCh_to_CIEXYZ(L, h, C))













class RetroPalette :
    
    convert = ColorConverter()
    
    def __init__(self, hue_offset=7, luminance_offset=2, hue_cycle=24, luminance_cycle=7, chroma=130, luminance_max=90, luminance_min=10, verbose=False) :
        self.luminance_min = luminance_min
        self.luminance_max = luminance_max
        self.chroma = chroma
        self.hue_cycle = hue_cycle
        self.hue_offset = hue_offset
        self.luminance_cycle = luminance_cycle
        self.luminance_offset = luminance_offset
        
        if verbose :
            self.demo(3)
    
    def L_level(self, t) :
        
        x = 7 * np.divmod((np.array(t)+self.luminance_offset)/self.luminance_cycle,1)[1]
        
        L = np.zeros(np.shape(t))
        
        
        L_min = self.luminance_min + 4 
        L_max = self.luminance_max - 4
        
        
        
        a, b = 6, (6*(L_min-L_max) + (L_max)*6.5 - 3.5*(L_min)) / (6.5-3.5)
        c, d = 7, self.luminance_min
        L[x < 7] = (x[x < 7]*(d-b) + b*c - a*d) / (c-a)
        
        a, b = 3.5, L_max
        c, d = 6.5, L_min
        L[x < 6] = (x[x < 6]*(d-b) + b*c - a*d) / (c-a)
        
        a, b = 3, self.luminance_max
        c, d = 4, (4*(L_min-L_max) + L_max*6.5 - 3.5*L_min) / (6.5-3.5)
        L[x < 4] = (x[x < 4]*(d-b) + b*c - a*d) / (c-a)
        
        a, b = 2, (2*(L_max-L_min) + 3*L_min - 0*L_max) / (3-0)
        c, d = 3, self.luminance_max
        L[x < 3] = (x[x < 3]*(d-b) + b*c - a*d) / (c-a)
        
        a, b = 0, L_min
        c, d = 3, L_max
        L[x < 2] = (x[x < 2]*(d-b) + b*c - a*d) / (c-a)
        
        a, b = 0, self.luminance_min
        c, d = 1, (1*(L_max-L_min) + 3*L_min - 0*L_max) / (3-0)
        L[x < 1] = (x[x < 1]*(d-b) + b*c - a*d) / (c-a)
        
        return L





    def hLC_values(self, t) :
        luminance = self.L_level(np.array(t) + self.luminance_offset)
        hue = 2 * π * np.divmod((np.array(t) + self.hue_offset)/self.hue_cycle,1)[1] - π / 10
        chroma = self.chroma * np.ones(np.shape(t))
        return np.moveaxis([luminance, self.h_level(hue), chroma],0,0)
    
    def h_level(self, h, x=0.5) :
        Θ = 5*π/4 # The angle around which we want to contract the colors
        θ = h - Θ + π
        k = np.floor( (θ+π)/(2*π) )
        φ = θ - 2*π*k
        h = φ * np.abs(φ/π)**x + Θ + π    
        return h


    def sRGB_values(self, t) :
        return self.convert.CIELCh_to_sRGB(*self.hLC_values(t))
    def RGB(self, t) :
        return self.sRGB_values(t)


    def hex_values(self, t) :
        return self.convert.sRGB_to_hex_unbound(*self.sRGB_values(t))
    def __call__(self, t, *args, **kwargs) :
        return self.hex_values(t)
    
    
    def demo(self, k=2) :
        cycle = max([abs(self.hue_cycle), abs(self.luminance_cycle)])
        x1 = np.linspace(0, np.ceil(k*cycle), 10001)
        x2 = np.arange(k*cycle+1)
        
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.scatter(x1, 300*self.hLC_values(x1)[2], 1, c=self.hex_values(x1))
        ax.scatter(x2, 300*self.hLC_values(x2)[2], c=self.hex_values(x2))
        ax.set_xlim(left=0)
        ax.set_ylim(bottom=0)
        ax.set_ylabel("Chroma")
        ax.set_xlabel("t")
        plt.show()
        
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.scatter(x1, 100*self.hLC_values(x1)[0], 1, c=self.hex_values(x1))
        ax.scatter(x2, 100*self.hLC_values(x2)[0], c=self.hex_values(x2))
        ax.set_xlim(left=0)
        ax.set_ylim(bottom=0)
        ax.set_ylabel("Luminance")
        ax.set_xlabel("t")
        plt.show()
















class ColorPalette :
    
    chroma_max = 60
    polynomial61 = lagrange_polynomial((200, 84), (247, 65), (331, 82))
    polynomial62 = lagrange_polynomial((111, 97), (145, 88), (200, 84))
    polynomial63 = lagrange_polynomial((-29, 82), (0, 72), (111, 97))
    
    chroma_max = 100
    polynomial101 = lagrange_polynomial((195, 79), (257, 43), (330, 71))
    polynomial102 = lagrange_polynomial((113, 96), (158, 82), (195, 79))
    polynomial103 = lagrange_polynomial((-30, 71), (0, 59), (56, 59), (113, 96))
    
    chroma_max = 140
    polynomial141 = lagrange_polynomial((194, 74), (257, 24), (332, 62))
    polynomial142 = lagrange_polynomial((115, 95), (158, 78), (194, 74))
    polynomial143 = lagrange_polynomial((-28, 62), (0, 49), (23, 45), (92, 67), (115, 95))
    
    chroma_max = 180
    polynomial181 = lagrange_polynomial((193, 71), (257, 7 ), (332, 54))
    polynomial182 = lagrange_polynomial((116, 95), (158, 75), (193, 71))
    polynomial183 = lagrange_polynomial((-28, 54), (0, 42), (23, 37), (90, 59), (116, 95))
    
    chroma_upper_bound = 190
    luminance_upper_bound = 90
    
    convert = ColorConverter()
    
    def __init__(self, hue_offset=0, luminance_offset=0, hue_cycle=37/2, luminance_cycle=8, chroma_max=140, luminance_max=70, chroma_min=1000, luminance_min=1000, slope=.99, marge=10, verbose=False) :
        self.luminance_min = luminance_min
        self.luminance_max = luminance_max
        self.chroma_min = chroma_min
        self.chroma_max = chroma_max
        self.hue_cycle = hue_cycle
        self.hue_offset = hue_offset
        self.luminance_cycle = luminance_cycle
        self.luminance_offset = luminance_offset
        self.slope = slope
        if marge > self.xmax/2 :
            self.marge = self.xmax/2
        else :
            self.marge = marge
        if verbose :
            print("Palette created")
            self.demo(3)
    
    
    
    
    def demo(self, k=2) :
        cycle = max([abs(self.hue_cycle), abs(self.luminance_cycle)])
        x1 = np.linspace(0, np.ceil(k*cycle), 10001)
        x2 = np.arange(k*cycle+1)
        
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.scatter(x1, 300*self.hLC_values(x1)[2], 1, c=self.hex_values(x1))
        ax.scatter(x2, 300*self.hLC_values(x2)[2], c=self.hex_values(x2))
        ax.set_xlim(left=0)
        ax.set_ylim(bottom=0)
        ax.set_ylabel("Chroma")
        ax.set_xlabel("t")
        plt.show()
        
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.scatter(x1, 100*self.hLC_values(x1)[0], 1, c=self.hex_values(x1))
        ax.scatter(x2, 100*self.hLC_values(x2)[0], c=self.hex_values(x2))
        ax.set_xlim(left=0)
        ax.set_ylim(bottom=0)
        ax.set_ylabel("Luminance")
        ax.set_xlabel("t")
        plt.show()
    
    def fingerprint(self, k=2) :
        self.demo(k)
        self.colorwheels()
    
    def colorwheels(self) :
        l0 = np.linspace(self.luminance_min, self.luminance_max, 401)
        H0 = np.linspace(0, 360, 180, endpoint=False)
        H, l = np.meshgrid(H0, l0)
        H = H.flatten()
        l = l.flatten()
        B = self.compute_B(H)
        c_ascending = self.chroma_ascending_luminance(l,B)
        c_descending = self.chroma_descending_luminance(l,B)
        
        fig = plt.figure()
        ax  = fig.add_subplot(111, projection="polar")
        fig.suptitle("Ascending luminances")
        colors_ascending = self.convert.OkLCh_to_hex(l/100,H*π/180,c_ascending/300)
        ax.scatter(H*π/180, c_ascending, 1, c=colors_ascending)
        plt.show()
        
        fig = plt.figure()
        ax  = fig.add_subplot(111, projection="polar")
        fig.suptitle("Descending luminances")
        colors_descending = self.convert.OkLCh_to_hex(l/100,H*π/180,c_descending/300)
        ax.scatter(H*π/180, c_descending, 1, c=colors_descending)
        plt.show()
        
    
    
    A = property(lambda s : s.Ctop * 3/4)
    xmax = property(lambda s : s.luminance_max - s.luminance_min)
    beta = property(lambda s : 2 * s.kappa * np.sqrt(s.xmax))
    Ctop = property(lambda s : s.chroma_max - s.chroma_min)
    kappa = property(lambda s : s.A / s.xmax)
    tipping_point = property(lambda s : 30 - 2*(s.chroma_max >= 140) - (s.chroma_max < 100) )
    
    
    @property
    def luminance_max(self) :
        return min([self.luminance_upper_bound, self._Lmax])
    @luminance_max.setter
    def luminance_max(self, L) :
        self._Lmax = L
        
        
    @property
    def chroma_min(self) :
        return min([180 - 2*self.luminance_max, self._Cmin])
    @chroma_min.setter
    def chroma_min(self, C) :
        self._Cmin = C
        
        
    @property
    def chroma_max(self) :
        return min([self.chroma_upper_bound, self._Cmax])
    @chroma_max.setter
    def chroma_max(self, C) :
        self._Cmax = C
    
    
    @property
    def luminance_min(self) :
        if self.chroma_max >= 180 :
            return min([5, self._Lmin])
        elif self.chroma_max >= 140 :
            return min([20, self._Lmin])
        elif self.chroma_max >= 100 :
            return min([40, self._Lmin])
        elif self.chroma_max >= 60 :
            return min([60, self._Lmin])
        return min([80, self._Lmin])
    @luminance_min.setter
    def luminance_min(self, L) :
        self._Lmin = L
    
    
    @property
    def slope(self) :
        if self.chroma_max >= 180 :
            return min([0.002, self._coeff])
        elif self.chroma_max >= 140 :
            return min([0.05, self._coeff])
        elif self.chroma_max >= 100 :
            return min([0.1, self._coeff])
        elif self.chroma_max >= 60 :
            return min([0.7, self._coeff])
        return min([0.6, self._coeff])
    @slope.setter
    def slope(self, s) :
        self._coeff = s


    def hLC_values(self, t) :
        d = 1 - 2*np.divmod((np.array(t)+self.luminance_offset)/self.luminance_cycle,1)[1]
        
        luminance = self.luminance_min + np.abs(d) * (self.luminance_max - self.luminance_min)
        hue_degres = 360 * np.divmod(-(np.array(t)+self.hue_offset)/self.hue_cycle,1)[1]
        chroma = np.zeros(np.shape(t))
        
        B = self.compute_B(hue_degres)
        chroma[d >= 0] = self.chroma_ascending_luminance(luminance[d >= 0],B[d >= 0])
        chroma[d < 0] = self.chroma_descending_luminance(luminance[d < 0],B[d < 0])
        return np.moveaxis([luminance/100, hue_degres*π/180, chroma/300],0,0)

        
    def compute_B(self, hue_degres) :
        reduced_hue = np.divmod(hue_degres+self.tipping_point,360)[1]-self.tipping_point
        a = self.P1(reduced_hue)
        b = self.P2(reduced_hue)
        c = self.P3(reduced_hue)
        return softmax([0.1, softmin([self.luminance_max, np.min(np.array([a,b,c]),axis=0)]) - self.luminance_min - self.marge])
    
    
    def P1(self, hue) :
        if self.chroma_max > 140 :
            return ColorPalette.polynomial181(hue)
        elif self.chroma_max > 100 :
            return ColorPalette.polynomial141(hue)
        elif self.chroma_max > 60 :
            return ColorPalette.polynomial101(hue)
        elif self.chroma_max > 30 :
            return ColorPalette.polynomial61(hue)
        return np.full(np.shape(hue), 80)
    def P2(self, hue) :
        if self.chroma_max > 140 :
            return ColorPalette.polynomial182(hue)
        elif self.chroma_max > 100 :
            return ColorPalette.polynomial142(hue)
        elif self.chroma_max > 60 :
            return ColorPalette.polynomial102(hue)
        elif self.chroma_max > 30 :
            return ColorPalette.polynomial62(hue)
        return np.full(np.shape(hue), 80)
    def P3(self, hue) :
        if self.chroma_max > 140 :
            return ColorPalette.polynomial183(hue)
        elif self.chroma_max > 100 :
            return ColorPalette.polynomial143(hue)
        elif self.chroma_max > 60 :
            return ColorPalette.polynomial103(hue)
        elif self.chroma_max > 30 :
            return ColorPalette.polynomial63(hue)
        return np.full(np.shape(hue), 80)
    
    
    def _run_tests(self) :
        self.fingerprint()
        self._test_hue()
        self._test_luminance()
        self._test_chroma()
    
    def _test_luminance(self) :
        H = np.linspace(0, 360, 181)
        c = np.linspace(0, self.chroma_max+5, 201)
        for L in np.linspace(self.luminance_min, self.luminance_max, 11) :
            fig = plt.figure()
            ax  = fig.add_subplot(111, projection="polar")

            fig.suptitle(f"Constant luminance L = {L}")

            x, y = np.meshgrid(H,c)
            x = x.reshape(len(H)*len(c))
            y = y.reshape(len(H)*len(c))
            
            colors = self.convert.OkLCh_to_hex(L/100,x*π/180,y/300)

            B = self.compute_B(H)
            ax.scatter(x*π/180, y, c=colors)
            
            ax.plot(H*π/180, self.chroma_descending_luminance(L,B))
            ax.plot(H*π/180, self.chroma_ascending_luminance(L,B),"k")

            plt.show()
    
    def _test_hue(self) :
        l = np.linspace(0, self.luminance_max+5, 101)
        c = np.linspace(0, self.chroma_max+5, 151)
        for h in np.linspace(0, 360, 12, endpoint=False) :
            fig = plt.figure()
            ax  = fig.add_subplot(111)

            fig.suptitle(f"Constant hue h = {h}°")

            x, y = np.meshgrid(c,l)
            x = x.reshape(len(c)*len(l))
            y = y.reshape(len(c)*len(l))

            colors = self.convert.OkLCh_to_hex(y/100,h*π/180,x/300)

            ax.scatter(x, y, c=colors)

            B = self.compute_B(h)
            ax.set_title(f"B = {B}")

            ax.plot(c[(c>=self.chroma_min)&(c<=self.chroma_max)], self.luminance_descending_chroma(c[(c>=self.chroma_min)&(c<=self.chroma_max)],B),"b")
            ax.plot(c[c>=self.chroma_min], self.luminance_ascending_chroma(c[c>=self.chroma_min],B),"k")

            ax.set_ylim(bottom=0, top=self.luminance_max+5)
            ax.set_xlim(left=0, right=self.chroma_max+5)
            
            ax.set_xlabel("Chroma")
            ax.set_ylabel("Luminance")
            plt.show()
    
    def _test_chroma(self) :
        l = np.linspace(0, self.luminance_max+5, 201)
        H = np.linspace(0, 360, 181)
        for C in np.linspace(self.chroma_min, self.chroma_max, 11) :

            fig = plt.figure()
            ax  = fig.add_subplot(111, projection="polar")

            fig.suptitle(f"Constant chroma C = {C}")

            x, y = np.meshgrid(H,l)
            x = x.reshape(len(H)*len(l))
            y = y.reshape(len(H)*len(l))
            
            colors = self.convert.OkLCh_to_hex(y/100,x*π/180,C/300)

            ax.scatter(x*π/180, y, c=colors)
            
            B = self.compute_B(H)
            ax.plot(H*π/180, self.luminance_ascending_chroma(C,B))
            ax.plot(H*π/180, self.luminance_descending_chroma(C,B),"b")

            plt.show()


    def chroma_ascending_luminance(self, luminance, border=34) :
        xL = np.array(luminance) - self.luminance_min
        if np.isscalar(border) and not np.isscalar(xL) :
            border = np.full(np.shape(xL), border)
        elif np.isscalar(xL) and not np.isscalar(border) :
            xL = np.full(np.shape(border), xL)

        def func_below_B(x, B) :
            b = self.xmax - B
            p = (self.slope+1) * self.Ctop / b
            E = np.abs(b*b*p - b*self.Ctop) / np.sqrt(2*b*self.Ctop*p - b*b*p*p)
            D = (p/b) * (E*E + b*b)
            alpha = (p/b) * np.sqrt(E*E+b*b)
            gamma = (self.Ctop-self.A) / np.abs(B)
            return self.chroma_min + self.A + gamma * np.sqrt(np.abs(B**2 - (x-B)**2))
        def func_above_B(x, B) :
            b = self.xmax - B
            p = (self.slope+1) * self.Ctop / b
            E = np.abs(b*b*p - b*self.Ctop) / np.sqrt(2*b*self.Ctop*p - b*b*p*p)
            D = (p/b) * (E*E + b*b)
            alpha = (p/b) * np.sqrt(E*E+b*b)
            gamma = (self.Ctop-self.A) / np.abs(B)
            return self.chroma_min + D - alpha * np.sqrt(E**2 + (x-B)**2)
        
        if np.isscalar(xL) and xL > border :
            return func_above_B(xL, border)
        elif np.isscalar(xL) :
            return func_below_B(xL, border)
        
        result = np.zeros(np.shape(xL))
        result[xL > border] = func_above_B(xL[xL > border], border[xL > border])
        result[xL <= border] = func_below_B(xL[xL <= border], border[xL <= border])
        return result


    def chroma_descending_luminance(self, luminance, border=34) :
        xL = np.array(luminance) - self.luminance_min
        if np.isscalar(xL) and not np.isscalar(border) :
            xL = np.full(np.shape(border), xL)
        return self.chroma_min + self.A * (1 - 2*np.sqrt(np.abs(xL/self.xmax)) + xL/self.xmax)


    def luminance_ascending_chroma(self, chroma, border=34) :
        yC = np.array(chroma) - self.chroma_min
        if np.isscalar(border) and not np.isscalar(yC) :
            border = np.full(np.shape(yC), border)
        elif np.isscalar(yC) and not np.isscalar(border) :
            yC = np.full(np.shape(border), yC)

        def func_below_A(y, B) :
            b = self.xmax - B
            p = (self.slope+1) * self.Ctop / b
            E = np.abs(b*b*p - b*self.Ctop) / np.sqrt(2*b*self.Ctop*p - b*b*p*p)
            D = (p/b) * (E*E + b*b)
            alpha = (p/b) * np.sqrt(E*E+b*b)
            gamma = (self.Ctop-self.A) / np.abs(B)
            return self.luminance_min + self.xmax * (1 - np.sqrt(y/self.A))**2
        def func_above_A(y, B) :
            b = self.xmax - B
            p = (self.slope+1) * self.Ctop / b
            E = np.abs(b*b*p - b*self.Ctop) / np.sqrt(2*b*self.Ctop*p - b*b*p*p)
            D = (p/b) * (E*E + b*b)
            alpha = (p/b) * np.sqrt(E*E+b*b)
            gamma = (self.Ctop-self.A) / np.abs(B)
            return self.luminance_min + B - np.sqrt(B**2 - ((y-self.A)/gamma)**2)
        
        if np.isscalar(yC) and yC > self.A :
            return func_above_A(yC, border)
        elif np.isscalar(yC) :
            return func_below_A(yC, border)
        
        result = np.zeros(np.shape(yC))
        result[yC > self.A] = func_above_A(yC[yC > self.A], border[yC > self.A])
        result[yC <= self.A] = func_below_A(yC[yC <= self.A], border[yC <= self.A])
        return result


    def luminance_descending_chroma(self, chroma, border=34) :
        B = border
        b = self.xmax - B
        p = (self.slope+1) * self.Ctop / b
        E = np.abs(b*b*p - b*self.Ctop) / np.sqrt(2*b*self.Ctop*p - b*b*p*p)
        D = (p/b) * (E*E + b*b)
        alpha = (p/b) * np.sqrt(E*E+b*b)
        gamma = (self.Ctop-self.A) / np.abs(B)
        yC = np.array(chroma) - self.chroma_min
        return self.luminance_min + B + np.sqrt(((yC-D)/alpha)**2 - E*E)


    def sRGB_values(self, t) :
        return self.convert.OkLCh_to_sRGB(*self.hLC_values(t))
    def RGB(self, t) :
        return self.sRGB_values(t)


    def hex_values(self, t) :
        return self.convert.sRGB_to_hex(*self.sRGB_values(t))
    def __call__(self, t, *args, **kwargs) :
        return self.hex_values(t)



palette_V = ColorPalette(hue_cycle=37/2, luminance_cycle=8, verbose=False)

periodic_wide_palette = ColorPalette(26/3, 3, hue_cycle=19/3, luminance_cycle=19, chroma_max=180)
periodic_palette = ColorPalette(0, 0, hue_cycle=11/3, luminance_cycle=11, chroma_max=180)
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=periodic_palette([5*i for i in range(periodic_palette.luminance_cycle)]))

palette_G = ColorPalette(hue_cycle=37/6, luminance_cycle=23/5)

palette_DS = ColorPalette(1.5, hue_cycle=-37/5, luminance_cycle=8/3)


old_palette_GrS3 = RetroPalette(luminance_offset=2, luminance_cycle=7/4, hue_offset=7/4, hue_cycle=24/4)





palette_V_lighter = copy.copy(palette_V)
palette_V_lighter.luminance_max = 75
palette_V_lighter.chroma_max = 100

palette_V_darker = copy.copy(palette_V)
palette_V_darker.luminance_max = 50
palette_V_darker.luminance_min = 10
palette_V_darker.chroma_max = 165





palette_G_lighter = copy.copy(palette_G)
palette_G_lighter.luminance_max = 75
palette_G_lighter.chroma_max = 100

palette_G_darker = copy.copy(palette_G)
palette_G_darker.luminance_max = 50
palette_G_darker.luminance_min = 10
palette_G_darker.chroma_max = 165





palette_DS_lighter = copy.copy(palette_DS)
palette_DS_lighter.luminance_max = 75
palette_DS_lighter.chroma_max = 100

palette_DS_darker = copy.copy(palette_DS)
palette_DS_darker.luminance_max = 50
palette_DS_darker.luminance_min = 10
palette_DS_darker.chroma_max = 165

if __name__ == "__main__" :
    for k in range(7) :
        old_palette_GrS3(k)