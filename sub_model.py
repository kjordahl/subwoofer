#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Subwoofer modeling tool

Author: Kelsey Jordahl
Version: alpha
Copyright: Kelsey Jordahl 2012
License: GPLv3
Time-stamp: <Fri Jul  6 19:14:47 EDT 2012>

    This program is free software: you can redistribute it and/or
    modify it under the terms of the GNU General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.  A copy of the GPL
    version 3 license can be found in the file COPYING or at
    <http://www.gnu.org/licenses/>.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

"""
import ConfigParser
import numpy as np
import matplotlib.pyplot as plt
from traits.api import (HasTraits, Int, Float, Bool, Enum, Str,
                        List, Range, Array, on_trait_change)
from frequency_plot import FrequencyPlot

class Enclosure(HasTraits):
    """Base class for a speaker enclosure"""
    Vb = Float
    Lv = Float
    Fb = Float
    F3 = Float
    dBpeak = Float
    Ql = Float(7)
    Vmin = Float(10)
    Vmax = Float(150)
    Fmin = 20                           # min F, Hz
    Fmax = 400                          # max F, Hz
    nF = 100                            # number of F values to sample for graph

    def __init__(self, driver):
        self.driver = driver
        self.F = np.logspace(np.log10(self.Fmin), np.log10(self.Fmax), self.nF)
        self.calculate_box()
        self.calculate_response()

    def set_plot(self, plot):
        self.plot = plot

    def calculate_box(self):
        raise NotImplementedError

    def calculate_response(self):
        raise NotImplementedError

    def _Vb_changed(self):
        self.calculate_response()
        try:
            self.plot.update_plotdata()
        except AttributeError:
            pass

class PortedEnclosure(Enclosure):
    """Calculate response for a ported enclosure
    http://www.diysubwoofers.org/prt
    """
    Dv = Float(3.0 * 2.54)              # 3 inch tube
    Np = Int(1)
    k = Float(0.732)

    def calculate_box(self):
        self.Vb = 20 * self.driver.Qts**3.3 * self.driver.Vas

    def min_port_diam(self):
        # port calculation
        Sd = np.pi * (self.driver.Dia * 2.54 / 100)**2 / 4
        Vd = Sd * self.driver.Xmax / 1000
        self.Dmin = 100 * (20.3 * (Vd**2 / self.Fb)**0.25) / self.Np**0.5
        # length of port (cm)
        self.Lv = (23562.5 * self.Dv**2 * self.Np /
                   (self.Fb**2 * self.Vb)) - (self.k * self.Dv)

    def calculate_response(self):
        self.Fb = (self.driver.Vas / self.Vb)**0.31 * self.driver.Fs
        self.min_port_diam()
        self.F3 = (self.driver.Vas / self.Vb)**0.44 * self.driver.Fs
        self.dBpeak = 20 * np.log(self.driver.Qts * (self.driver.Vas / self.Vb) ** 0.3 / 0.4)
        Fn2 = (self.F / self.driver.Fs) ** 2
        Fn4 = Fn2 ** 2
        A = (self.Fb / self.driver.Fs) ** 2
        B = A / self.driver.Qts + self.Fb / (self.driver.Fs * self.Ql)
        C = 1 + A + (self.driver.Vas / self.Vb) + self.Fb / (self.driver.Fs * self.driver.Qts * self.Ql)
        D = 1 / self.driver.Qts + self.Fb / (self.driver.Fs * self.Ql)
        self.dBmag = 10 * np.log(Fn4**2 / ((Fn4 - C * Fn2 + A)**2 + Fn2 * (D * Fn2 - B)**2))

    def _Dv_changed(self):
        try:
            self.calculate_response()
            self.plot.update_plotdata()
        except AttributeError, er:
            print er

        
class SealedEnclosure(Enclosure):
    """Calculate response for a sealed enclosure
    http://www.diysubwoofers.org/sld
    NOT YET WORKING
    """
    Vmin = Float(3)
    Vmax = Float(50)
    Qtc = Float(0.7)
    # http://www.ajdesigner.com/phpsubwooferclosed/resonance_frequency_equation_qts.php
    # these don't make sense for a sealed enlosure, but GUI doesn't know that yet
    Dv = Float(1)
    Dmin = Float(0)

    def calculate_box(self):
        self.Qr = self.Qtc / self.driver.Qts
        self.Vr = self.Qr**2 - 1
        self.Vb = self.driver.Vas / self.Vr

    def calculate_response(self):
        self.Fb = self.Qr * self.driver.Fs
        self.Qtc = self.Fb * self.driver.Qts / self.driver.Fs
        self.F3 = self.Fb * ((1 / self.Qtc**2 - 2 +
                         ((1 / self.Qtc**2 - 2)**2 + 4)**0.5) / 2)**0.5
        if self.Qtc > np.sqrt(0.5):
            dBpeak = 20 * np.log(self.Qtc**2 / (self.Qtc**2 - 0.25)**0.5)
        else:
            dBpeak = 0
        Fr = (self.F / self.Fb)**2
        self.dBmag = 10 * np.log(Fr**2 / ((Fr - 1)**2 + Fr / self.Qtc**2))

    def _Vb_changed(self):
        self.Vr = self.driver.Vas / self.Vb
        self.Qr = np.sqrt(self.Vr + 1)
        super(SealedEnclosure, self)._Vb_changed()

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
    sub = PortedEnclosure(driver)
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
