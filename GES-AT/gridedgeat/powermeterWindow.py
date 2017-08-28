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
from PyQt5.QtWidgets import (QLabel, QLineEdit, QCheckBox, QWidget, QMainWindow, QPushButton, QApplication)
from .modules.powermeter import *

class PowermeterWindow(QMainWindow):
    def __init__(self, parent=None):
        super(PowermeterWindow, self).__init__(parent)
        self.initUI(self)
    
    def initUI(self, PowermeterWindow):
        self.setGeometry(10, 200, 320, 90)
        self.powerMeterLabel = QLabel(PowermeterWindow)
        self.powerMeterLabel.setGeometry(QRect(20, 20, 300, 16))
        PowermeterWindow.setWindowTitle("Powermeter Settings")
        self.powermeterButton = QPushButton(PowermeterWindow)
        self.powermeterButton.setGeometry(QRect(10, 50, 300, 30))
        self.powermeterButton.clicked.connect(self.powerConnect)
        self.powermeterButton.setText("Start")
        self.pm = PowerMeter()
        
        if self.pm.PM100init is False:
            self.powermeterButton.setEnabled(False)
            self.powerMeterLabel.setText("Powermeter libraries or connection failed")
        else:
            self.powerMeterLabel.setText("Powermeter connection OK")


    def powerConnect(self):
        while True:
            self.powerMeterLabel.setText("Power levels [mW]: <qt><b>{0:0.4f}</b></qt>".format(1000*self.pm.get_power().read))
            time.sleep(0.5)
            QApplication.processEvents()
            print("Power levels [mW]: {0:0.4f}".format(1000*self.pm.get_power().read))
            
        
