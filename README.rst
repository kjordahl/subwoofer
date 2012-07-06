Subwoofer modeling
==================
This is a simple tool for modeling the frequency response of a subwoofer enclosure with a given driver.  By interactively adjusting the volume of the enclosure, the user can immediately see the change in frequency response.  The equations used for modeling the behavior are based on those at `http://www.diysubwoofers.org`.

Files
-----
* README.rst: This file
* COPYING: GPL v3 license
* sub_model.py: The main Python program file. Run this to start the model.
* params.cfg: Driver parameters. Edit this file to add new drivers.
* sub_view.enaml: Enaml GUI file
* frequency_plot.py: Chaco plotting tools

Requirements
------------
* Python 2.6 or 2.7
* NumPy
* `Traits <http://code.enthought.com/projects/traits>`
* `Enaml <https://github.com/enthought/enaml>`
* `Chaco <http://code.enthought.com/projects/chaco>`

All of the above requirements are met by the `Enthought Python Distribution (EPD) <http://www.enthought.com/products/epd.php>`, including `EPD Free <http://www.enthought.com/products/epd_free.php>`.
