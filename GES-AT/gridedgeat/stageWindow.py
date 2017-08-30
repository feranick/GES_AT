'''
stageWindow
------------------
Class for providing a graphical user interface for 
XY stage panel

Copyright (C) 2017 Nicola Ferralis <ferralis@mit.edu>
Copyright (C) 2017 Auto-testing team - MIT GridEdge Solar

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

'''

from PyQt5.QtCore import QRect
from PyQt5.QtWidgets import (QLabel, QPushButton, QWidget, QMainWindow, QApplication)
from .modules.xystage.xystage import *

class StageWindow(QMainWindow):
    def __init__(self, parent=None):
        super(StageWindow, self).__init__(parent)
        self.initUI(self)
    
    def initUI(self, StageWindow):
        StageWindow.resize(330, 100)
        StageWindow.setWindowTitle("XY stage control settings")

        self.stageLabel = QLabel(StageWindow)
        self.stageLabel.setGeometry(QRect(20, 20, 300, 20))

        self.homingButton = QPushButton(StageWindow)
        self.homingButton.setGeometry(QRect(10, 50, 140, 40))
        self.homingButton.setText("Move Home")
        self.homingButton.clicked.connect(self.moveHome)
        
        self.setCurPositOriginButton = QPushButton(StageWindow)
        self.setCurPositOriginButton.setGeometry(QRect(160, 50, 140, 40))
        self.setCurPositOriginButton.setText("Set Origin")
        self.setCurPositOriginButton.clicked.connect(self.setCurrentPosOrigin)
        
        self.xystage = XYstage()
        
        if self.xystage.xystageInit is False:
            self.homingButton.setEnabled(False)
            self.setCurPositOriginButton.setEnabled(False)
            self.stageLabel.setText("XYstage libraries or connection failed")
        else:
            self.stageLabel.setText("XYstage connection OK")

    def moveHome(self):
        self.stageLabel.setText("Moving stage to home position...")
        QApplication.processEvents()
        self.xystage.move_home()
        self.stageLabel.setText("Ready")

    
    def setCurrentPosOrigin(self):
        self.stageLabel.setText("Setting current position as origin")
        QApplication.processEvents()
        self.xystage.set_origin(True, (_,_))


