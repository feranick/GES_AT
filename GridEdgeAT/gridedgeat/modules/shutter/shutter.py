'''
shutter.py
-------------
Class for providing a hardware support for 
for the the solar Sim shutter via TTL-FTDI

Copyright (C) 2017-2018 Nicola Ferralis <ferralis@mit.edu>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

Manual for cable wiring:
http://www.ftdichip.com/Support/Documents/DataSheets/Cables/DS_TTL-232R_CABLES.pdf
    Black  -> GND
    Brown  -> CTS
    Red    -> VCC (5V continuous)
    Orange -> TXD
    Yellow -> RXD
    Green  -> RTS
    
Shutter should be connected to RTS and GND
'''
import ftd2xx

####################################################################
# Shutter low-level class
####################################################################
class Shutter():
    # Define connection to powermeter
    def __init__(self):
        try:
            self.shutter = ftd2xx.open(0)
            self.shutter.setTimeouts(1000,1000)
            self.closed()
        except:
            pass

    def __del__(self):
        try:
            self.shutter.close()
        except:
            pass

    # Open the shutter (0V)
    def open(self):
        self.shutter.clrRts()

    # Close the shutter (5V)
    def closed(self):
        self.shutter.setRts()


