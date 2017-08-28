'''
powermeter.py
-------------
Class for providing a hardware support for 
for the powermeter Thorlabs PM100

Copyright (C) 2017 Michel Nasilowski <micheln@mit.edu>
Copyright (C) 2017 Nicola Ferralis <ferralis@mit.edu>
Copyright (C) 2017 Auto-testing team - MIT GridEdge Solar

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

'''

import time
from .. import config
from ThorlabsPM100 import ThorlabsPM100
import visa

class PowerMeter():
    def __init__(self):
        try:
            self.rm = visa.ResourceManager()
            self.PM100init = True
        except:
            self.PM100init = False
        time.sleep(1)

    def get_power(self):
        inst = self.rm.open_resource(config.powermeterID, timeout=1)
        power_meter = ThorlabsPM100(inst=inst)
        return power_meter
