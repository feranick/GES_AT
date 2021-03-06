'''
sourcemeterWindow
------------------
Class for providing a graphical user interface for 
sourcemeter

Copyright (C) 2017-2019 Nicola Ferralis <ferralis@mit.edu>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

'''

import time
from PyQt5.QtCore import (QRect,QObject, QThread, pyqtSlot, pyqtSignal)
from PyQt5.QtWidgets import (QLabel, QLineEdit, QCheckBox, QWidget,
                             QMainWindow,QPushButton)
from .modules.sourcemeter.sourcemeter import *

####################################################################
# Source meter control window
####################################################################
class SourcemeterWindow(QMainWindow):
    def __init__(self, parent=None):
        super(SourcemeterWindow, self).__init__(parent)
        self.initUI(self)
    
    # Setup UI elements
    def initUI(self, SourcemeterWindow):
        self.setGeometry(10, 290, 340, 150)
        SourcemeterWindow.setWindowTitle("Sourcemeter controls")
        self.setFixedSize(self.size())
        self.sourcemeterVoltageLabel = QLabel(SourcemeterWindow)
        self.sourcemeterVoltageLabel.setGeometry(QRect(20, 10, 120, 20))
        self.sourcemeterVoltageLabel.setText("Voltage: ")
        self.sourcemeterVoltageText = QLineEdit(SourcemeterWindow)
        self.sourcemeterVoltageText.setGeometry(QRect(80, 10, 50, 20))
        self.sourcemeterVoltageText.setText("1")
        
        self.sourcemeterVoltageReadLabel = QLabel(SourcemeterWindow)
        self.sourcemeterVoltageReadLabel.setGeometry(QRect(20, 40, 300, 20))
        self.sourcemeterVoltageReadLabel.setText("")
        
        self.sourcemeterCurrentReadLabel = QLabel(SourcemeterWindow)
        self.sourcemeterCurrentReadLabel.setGeometry(QRect(20,70, 300, 20))
        self.sourcemeterCurrentReadLabel.setText("Ready")
        
        self.startSourcemeterButton = QPushButton(SourcemeterWindow)
        self.startSourcemeterButton.setGeometry(QRect(10, 100, 150, 40))
        self.startSourcemeterButton.setText("Start")
        self.startSourcemeterButton.clicked.connect(self.startSourcemeter)
    
        self.stopSourcemeterButton = QPushButton(SourcemeterWindow)
        self.stopSourcemeterButton.setGeometry(QRect(180, 100, 150, 40))
        self.stopSourcemeterButton.setText("Stop")
        self.stopSourcemeterButton.clicked.connect(self.stopSourcemeter)
        self.stopSourcemeterButton.setEnabled(False)

    # Start the thread for connecting and collecting basic V,I data
    def startSourcemeter(self):
        self.startSourcemeterButton.setEnabled(False)
        self.stopSourcemeterButton.setEnabled(True)
        self.smThread = sourcemeterThread(parent=self)
        self.smThread.smResponse.connect(lambda Vread, Cread, flag: self.printMsg(Vread, Cread, flag))
        self.smThread.start()
    
    # Logic to stop powermeter acquisition
    def stopSourcemeter(self):
        self.stopSourcemeterButton.setEnabled(False)
        self.startSourcemeterButton.setEnabled(True)
        self.sourcemeterVoltageReadLabel.setText("")
        self.sourcemeterCurrentReadLabel.setText("Sourcemeter stopped")
        try:
            if self.smThread.isRunning():
                self.smThread.stop()
        except:
            pass

    # Print output
    def printMsg(self, Vmsg, Cmsg, flag):
        self.sourcemeterVoltageReadLabel.setText(Vmsg)
        self.sourcemeterCurrentReadLabel.setText(Cmsg)
        print(str(Vmsg),"  ",str(Cmsg))
        if flag is False:
            self.startSourcemeterButton.setEnabled(True)
            self.stopSourcemeterButton.setEnabled(False)

    # Stop acquisition upon closing the powermeter window
    def closeEvent(self, event):
        self.stopSourcemeter()

####################################################################
# Main class thread for sourcemeter
####################################################################
class sourcemeterThread(QThread):
    smResponse = pyqtSignal(str, str, bool)
    
    def __init__(self, parent=None):
        super(sourcemeterThread, self).__init__(parent)
        self.maxV = 10

    def __del__(self):
        self.wait()

    def stop(self):
        self.runningFlag = False
        time.sleep(0.5)
        self.sc.set_output(voltage = 0)    
        self.sc.off()
        del self.sc
        self.terminate()

    def run(self):
        try:
            self.sc = SourceMeter(self.parent().parent().config.sourcemeterID)
            deviceArea = 1

            self.sc.set_limit(voltage=self.maxV, current=0.12)
            self.runningFlag = True
            while self.runningFlag is True:
                voltageText = self.parent().sourcemeterVoltageText.text()
                if voltageText == "" or voltageText == "-":
                    pass
                else:
                    self.sc.on()
                    voltage = float(voltageText)
                    self.sc.set_output(voltage = voltage)
                    self.smResponse.emit("Voltage [V]: "+str(self.sc.read_values(deviceArea)[0]), \
                        " Current [mA]: "+str(self.sc.read_values(deviceArea)[1]), True)
                    self.sc.off()
                time.sleep(0.2)
        except:
            self.smResponse.emit("","Cannot connect to sourcemeter", False)
