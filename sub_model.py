#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ConfigParser
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
    Fmin = 20                           # min F, Hz
    Fmax = 400                          # max F, Hz
    nF = 100                            # number of F values to sample for graph

    def __init__(self, driver):
        self.driver = driver
        self.F = np.logspace(np.log10(self.Fmin), np.log10(self.Fmax), self.nF)
        self.calculate_box()
        # port calculation
        # length of port (cm)
        self.Lv = (23562.5 * self.Dv**2 * self.Np /
                   (self.Fb**2 * self.Vb)) - (self.k * self.Dv)
        self.calculate_response()

    def set_plot(self, plot):
        self.plot = plot

    def calculate_box(self):
        self.Vb = 20 * self.driver.Qts**3.3 * self.driver.Vas

    def calculate_response(self):
        self.Fb = (self.driver.Vas / self.Vb)**0.31 * self.driver.Fs
        self.F3 = (self.driver.Vas / self.Vb)**0.44 * self.driver.Fs
        self.dBpeak = 20 * np.log(self.driver.Qts * (self.driver.Vas / self.Vb) ** 0.3 / 0.4)
        Fn2 = (self.F / self.driver.Fs) ** 2
        Fn4 = Fn2 ** 2
        A = (self.Fb / self.driver.Fs) ** 2
        B = A / self.driver.Qts + self.Fb / (self.driver.Fs * self.Ql)
        C = 1 + A + (self.driver.Vas / self.Vb) + self.Fb / (self.driver.Fs * self.driver.Qts * self.Ql)
        D = 1 / self.driver.Qts + self.Fb / (self.driver.Fs * self.Ql)
        self.dBmag = 10 * np.log(Fn4**2 / ((Fn4 - C * Fn2 + A)**2 + Fn2 * (D * Fn2 - B)**2))

    def _Vb_changed(self):
        self.calculate_response()
        try:
            self.plot.update_plotdata()
        except AttributeError:
            pass
        
class Driver(HasTraits):
    Vas = Float                  # compliance volume (liters)
    Qts = Float                  # Total Q
    Fs = Float                   # Free-air resonance (Hz)
    Xmax = Float                 # Max excursion, mm
    Dia = Float                  # driver diameter
    drivername = Str
    drivernames = List

    def __init__(self, drivername=None):
        if drivername is not None:
            self.drivername = drivername
        self.get_config()

    def set_enclosure(self, enclosure):
        self.enclosure = enclosure

    def get_config(self):
        self.config = ConfigParser.RawConfigParser()
        self.config.read('params.cfg')
        self.drivernames = self.config.sections()
        if self.drivername is None or not self.drivername in self.drivernames:
            self.drivername = self.drivernames[0]
        self.get_params()

    def get_params(self):
        self.Vas = self.config.getfloat(self.drivername, 'Vas')
        self.Qts = self.config.getfloat(self.drivername, 'Qts')
        self.Fs = self.config.getfloat(self.drivername, 'Fs')
        self.Xmax = self.config.getfloat(self.drivername, 'Xmax')
        self.Dia = self.config.getfloat(self.drivername, 'Dia')

    def _drivername_changed(self):
        try:
            self.get_params()
            self.enclosure.calculate_box()
            self.enclosure.calculate_response()
            self.enclosure.plot.update_plotdata()
        except AttributeError:
            pass                        # driver params not yet set

    @property
    def param_dict(self):
        config = ConfigParser.RawConfigParser()
        config.read('example.cfg')

def main():
    driver = Driver()
    sub = Enclosure(driver)
    driver.set_enclosure(sub)
    plot = FrequencyPlot(sub)
    sub.set_plot(plot)

    import enaml
    with enaml.imports():
        from sub_view import SubView
    view = SubView(model=sub, plot=plot)
    view.show()

if __name__ == '__main__':
    main()
