'''
sourcemeterWindow
------------------
Class for providing a graphical user interface for 
sourcemeter

Copyright (C) 2017 Nicola Ferralis <ferralis@mit.edu>
Copyright (C) 2017 Auto-testing team - MIT GridEdge Solar

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

'''

from PyQt5.QtCore import (QRect,QObject, QThread, pyqtSlot, pyqtSignal)
from PyQt5.QtWidgets import (QLabel, QLineEdit, QCheckBox, QWidget,
                             QMainWindow,QPushButton)
from .modules.sourcemeter.sourcemeter import *

class SourcemeterWindow(QMainWindow):
    def __init__(self, parent=None):
        super(SourcemeterWindow, self).__init__(parent)
        self.initUI(self)
    
    # Setup UI elements
    def initUI(self, SourcemeterWindow):
        self.setGeometry(10, 200, 320, 120)
        self.sourcemeterLabel = QLabel(SourcemeterWindow)
        self.sourcemeterLabel.setGeometry(QRect(20, 40, 300, 20))
        SourcemeterWindow.setWindowTitle("Sourcemeter controls")
        self.sourcemeterLabel.setText("Ready")

        self.sourcemeterVoltageLabel = QLabel(SourcemeterWindow)
        self.sourcemeterVoltageLabel.setGeometry(QRect(20, 10, 120, 20))
        self.sourcemeterVoltageLabel.setText("Voltage")
        self.sourcemeterVoltageText = QLineEdit(SourcemeterWindow)
        self.sourcemeterVoltageText.setGeometry(QRect(140, 10, 50, 20))
        self.sourcemeterVoltageText.setText("1")
        
        self.activateSourcemeterButton = QPushButton(SourcemeterWindow)
        self.activateSourcemeterButton.setGeometry(QRect(10, 70, 300, 40))
        self.activateSourcemeterButton.setText("Connect to Sourcemeter")
        self.activateSourcemeterButton.clicked.connect(self.activateSourcemeter)

    def activateSourcemeter(self):
        self.activateSourcemeterButton.setEnabled(False)
        self.smThread = sourcemeterThread(self)
        self.smThread.smResponse.connect(self.printMsg)
        self.smThread.start()

    def printMsg(self, msg):
        self.sourcemeterLabel.setText(msg)
        print(msg)
        self.activateSourcemeterButton.setEnabled(True)

class sourcemeterThread(QThread):

    smResponse = pyqtSignal(str)

    def __init__(self, parent_obj):
        QThread.__init__(self)
        self.parent_obj = parent_obj

    def __del__(self):
        self.wait()

    def stop(self):
        self.terminate()

    def run(self):
        try:
            sc = SourceMeter()
            sc.set_limit(voltage=10, current=0.12)
            sc.on()
            sc.set_output(voltage = float(self.parent_obj.sourcemeterVoltageText.text()))
            self.smResponse.emit("Voltage [V]: "+str(sc.read_values()[0])+\
                                 " Current [A]: "+str(sc.read_values()[1]))
            sc.off()
            del sc
        except:
            self.smResponse.emit("Cannot connect to sourcemeter")
            
        

