'''
powermeterWindow
------------------
Class for providing a graphical user interface for 
powermeter panel

Copyright (C) 2017 Nicola Ferralis <ferralis@mit.edu>
Copyright (C) 2017 Michel Nasilowski <micheln@mit.edu>
Copyright (C) 2017 Auto-testing team - MIT GridEdge Solar

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

'''

from PyQt5.QtCore import QRect
from PyQt5.QtWidgets import (QLabel, QLineEdit, QCheckBox, QWidget)
from .powermeter import *

class PowermeterWindow(QWidget):

    def __init__(self):
        super(PowermeterWindow, self).__init__()
        self.initUI(self)
    
    def initUI(self, PowermeterWindow):
        PowermeterWindow.resize(328, 60)
        self.powerMeterLabel = QLabel(PowermeterWindow)
        self.powerMeterLabel.setGeometry(QRect(20, 20, 300, 16))
        PowermeterWindow.setWindowTitle("Powermeter")

        pm = PowerMeter()
        if pm.PM100init is False:
            self.powerMeterLabel.setText("Powermeter libraries or connection failed")
        else:
            while True:
                self.powerMeterLabel.setText("Power levels [mW]: <qt><b>{0:0.4f}</b></qt>".format(1000*power_meter.read))
                time.sleep(1)
