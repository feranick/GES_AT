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
from PyQt5.QtWidgets import (QLabel, QLineEdit, QWidget, QMainWindow, QPushButton, QApplication)
from .modules.powermeter.powermeter import *

class PowermeterWindow(QMainWindow):
    def __init__(self, parent=None):
        super(PowermeterWindow, self).__init__(parent)
        self.initUI(self)
        self.activePowermeter = False
    
    def initUI(self, PowermeterWindow):
        PowermeterWindow.setWindowTitle("Powermeter Settings")
        self.setGeometry(10, 200, 320, 110)
        self.powerMeterRefreshLabel = QLabel(PowermeterWindow)
        self.powerMeterRefreshLabel.setGeometry(QRect(20, 10, 120, 20))
        self.powerMeterRefreshLabel.setText("Refresh every [s]:")
        self.powerMeterRefreshText = QLineEdit(PowermeterWindow)
        self.powerMeterRefreshText.setGeometry(QRect(140, 10, 50, 20))
        self.powerMeterRefreshText.setText("0.5")

        self.powerMeterLabel = QLabel(PowermeterWindow)
        self.powerMeterLabel.setGeometry(QRect(20, 40, 300, 20))        
        self.powermeterStartButton = QPushButton(PowermeterWindow)
        self.powermeterStartButton.setGeometry(QRect(10, 70, 140, 30))
        self.powermeterStartButton.clicked.connect(self.startPMAcq)
        self.powermeterStartButton.setText("Start")
        self.powermeterStopButton = QPushButton(PowermeterWindow)
        self.powermeterStopButton.setGeometry(QRect(170, 70, 140, 30))
        self.powermeterStopButton.clicked.connect(self.stopPMAcq)
        self.powermeterStopButton.setText("Stop")
        self.powermeterStopButton.setEnabled(False)

        self.powermeterStopButton.setEnabled(False)
        self.powermeterStartButton.setEnabled(True)

    def stopPMAcq(self):
        self.stopAcqFlag = True
        self.powermeterStopButton.setEnabled(False)
        self.powermeterStartButton.setEnabled(True)
        self.powerMeterLabel.setText("Powermeter stopped")


    def startPMAcq(self):
        if self.activePowermeter == False:
            self.powermeterStartButton.setEnabled(True)
            self.powerMeterLabel.setText("Activating Powermeter...")
            QApplication.processEvents()
            self.pm = PowerMeter(self.parent().config.powermeterID)
            
        if self.pm.PM100Init is False:
            self.powermeterStartButton.setEnabled(True)
            self.powermeterStopButton.setEnabled(False)
            self.powerMeterLabel.setText("Powermeter libraries or connection failed")
        else:
            self.activePowermeter = True
            self.powerMeterLabel.setText("Powermeter activated")
            self.powermeterStartButton.setEnabled(False)
            self.powermeterStopButton.setEnabled(True)
            self.stopAcqFlag = False
            while True:
                try:
                    self.powerMeterLabel.setText("Power levels [mW]: {0:0.4f}".format(1000*self.pm.get_power().read))
                    time.sleep(float(self.powerMeterRefreshText.text()))
                    QApplication.processEvents()
                    print("Power levels [mW]: {0:0.4f}".format(1000*self.pm.get_power().read))
                    if self.stopAcqFlag is True:
                        break
                except:
                    print("Connection failed")
                    break

    def closeEvent(self, event):
       self.stopPMAcq()    
        
