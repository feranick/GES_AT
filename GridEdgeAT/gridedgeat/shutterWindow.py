'''
shutterWindow
------------------
Class for providing a graphical user interface for 
manually controlling the shutter

Copyright (C) 2017-2018 Nicola Ferralis <ferralis@mit.edu>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

'''
import time
from PyQt5.QtCore import (QRect,QObject, QThread, pyqtSlot, pyqtSignal)
from PyQt5.QtWidgets import (QLabel, QLineEdit, QCheckBox,
                             QWidget,QMainWindow,QPushButton)
from .modules.shutter.shutter import *

class ShutterWindow(QMainWindow):
    def __init__(self, parent=None):
        super(ShutterWindow, self).__init__(parent)
        self.initUI(self)
    
    # define UI elements
    def initUI(self, ShutterWindow):
        self.setGeometry(10, 610, 340, 100)
        self.setFixedSize(self.size())
        
        self.shutterLabel = QLabel(ShutterWindow)
        self.shutterLabel.setGeometry(QRect(20, 20, 300, 20))
        ShutterWindow.setWindowTitle("Shutter controls")
        self.shutterLabel.setText("Ready")
        self.openShutterButton = QPushButton(ShutterWindow)
        self.openShutterButton.setGeometry(QRect(10, 50, 150, 40))
        self.openShutterButton.setText("Open Shutter")
        self.openShutterButton.clicked.connect(lambda: self.activateShutter(True))
        self.openShutterButton.setEnabled(True)

        self.closeShutterButton = QPushButton(ShutterWindow)
        self.closeShutterButton.setGeometry(QRect(170, 50, 150, 40))
        self.closeShutterButton.setText("Close Shutter")
        self.closeShutterButton.clicked.connect(lambda: self.activateShutter(False))
        self.closeShutterButton.setEnabled(False)

    # Activate shutter
    def activateShutter(self, open):
        try:
            shutter = Shutter()
            if open == True:
                shutter.open()
                msg = "Shutter OPEN"
                self.openShutterButton.setEnabled(False)
                self.closeShutterButton.setEnabled(True)
            else:
                shutter.closed()
                msg = "Shutter CLOSED"
                self.openShutterButton.setEnabled(True)
                self.closeShutterButton.setEnabled(False)
            time.sleep(0.5)
        except:
            msg = "Cannot connect to shutter"
        self.printMsg(msg)

    # Print status
    def printMsg(self, msg):
        self.shutterLabel.setText(msg)
        print(msg)

    # Close connection upon closing window.
    def closeEvent(self, event):
        self.activateShutter(False)

            
        
