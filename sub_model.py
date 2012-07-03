#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
from traits.api import (HasTraits, Int, Float, Bool, Enum, Str,
                        List, Range, Array)
from frequency_plot import FrequencyPlot

class Enclosure(HasTraits):
    # 3 inch tube
    Dv = Float(3.0 * 2.54)              # 3 inch tube
    Vb = Float
    Lv = Float
    Fb = Float
    F3 = Float
    dBpeak = Float
    Np = Int(1)
    Ql = Float(7)
    k = Float(0.732)

    def __init__(self, driver):
        self.driver = driver
        self.F = np.arange(20, 400, 2)
        self.Vb = 20 * driver.Qts**3.3 * driver.Vas
        self.calculate_box()
        # port calculation
        # length of port (cm)
        self.Lv = (23562.5 * self.Dv**2 * self.Np /
                   (self.Fb**2 * self.Vb)) - (self.k * self.Dv)
        self.calculate_response()

    def set_plot(self, plot):
        self.plot = plot

    def calculate_box(self):
        self.Fb = (self.driver.Vas / self.Vb)**0.31 * self.driver.Fs
        self.F3 = (self.driver.Vas / self.Vb)**0.44 * self.driver.Fs
        self.dBpeak = 20 * np.log(self.driver.Qts * (self.driver.Vas / self.Vb) ** 0.3 / 0.4)

    def calculate_response(self):
        Fn2 = (self.F / self.driver.Fs) ** 2
        Fn4 = Fn2 ** 2
        A = (self.Fb / self.driver.Fs) ** 2
        B = A / self.driver.Qts + self.Fb / (self.driver.Fs * self.Ql)
        C = 1 + A + (self.driver.Vas / self.Vb) + self.Fb / (self.driver.Fs * self.driver.Qts * self.Ql)
        D = 1 / self.driver.Qts + self.Fb / (self.driver.Fs * self.Ql)
        self.dBmag = 10 * np.log(Fn4**2 / ((Fn4 - C * Fn2 + A)**2 + Fn2 * (D * Fn2 - B)**2))

    def _Vb_changed(self):
        print self.Vb
        self.calculate_box()
        self.calculate_response()
        self.plot.update_plotdata()
        
class Driver(HasTraits):
    # Infinity 1260W technical reference data
    Vas = Float(82.96)                  # compliance volume (liters)
    Qts = Float(0.39)                   # Total Q
    Fs = Float(23.50)                   # Free-air resonance (Hz)
    Xmax = Float(13.00)                 # Max excursion, mm
    Dia = Float(12 * 2.54)              # 12-in driver

    def __init__(self):
        pass

def main():
    driver = Driver()
    sub = Enclosure(driver)
    plot = FrequencyPlot(sub)
    sub.set_plot(plot)

    import enaml
    with enaml.imports():
        from sub_view import SubView
    view = SubView(model=sub, plot=plot)
    view.show()

if __name__ == '__main__':
    main()
