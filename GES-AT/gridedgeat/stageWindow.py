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
from PyQt5.QtWidgets import (QLabel, QLineEdit, QPushButton, QWidget, QMainWindow, QApplication)
from .modules.xystage.xystage import *

class StageWindow(QMainWindow):
    def __init__(self, parent=None):
        super(StageWindow, self).__init__(parent)
        self.initUI(self)
    
    def initUI(self, StageWindow):
        StageWindow.resize(310, 250)
        StageWindow.setWindowTitle("XY stage control settings")

        self.stageLabel = QLabel(StageWindow)
        self.stageLabel.setGeometry(QRect(20, 20, 300, 20))

        self.homingButton = QPushButton(StageWindow)
        self.homingButton.setGeometry(QRect(10, 65, 110, 40))
        self.homingButton.setText("Move Home")
        self.homingButton.clicked.connect(self.moveHome)
        
        self.setCurPositOriginButton = QPushButton(StageWindow)
        self.setCurPositOriginButton.setGeometry(QRect(190, 65, 110, 40))
        self.setCurPositOriginButton.setText("Set Origin")
        self.setCurPositOriginButton.clicked.connect(self.setCurrentPosOrigin)
        
        self.upButton = QPushButton(StageWindow)
        self.upButton.setGeometry(QRect(120, 50, 70, 70))
        self.upButton.setText("UP")
        self.upButton.clicked.connect(lambda: self.moveStage(0,1))
        self.downButton = QPushButton(StageWindow)
        self.downButton.setGeometry(QRect(120, 170, 70, 70))
        self.downButton.setText("DOWN")
        self.downButton.clicked.connect(lambda: self.moveStage(0,-1))
        self.leftButton = QPushButton(StageWindow)
        self.leftButton.setGeometry(QRect(50, 110, 70, 70))
        self.leftButton.setText("LEFT")
        self.leftButton.clicked.connect(lambda: self.moveStage(-1,0))
        self.rightButton = QPushButton(StageWindow)
        self.rightButton.setGeometry(QRect(190, 110, 70, 70))
        self.rightButton.setText("RIGHT")
        self.rightButton.clicked.connect(lambda: self.moveStage(1,0))
        
        self.stepStageText = QLineEdit(StageWindow)
        self.stepStageText.setGeometry(QRect(135, 140, 40, 25))
        self.stepStageText.setText("0.1")
        self.stepStageLabel = QLabel(StageWindow)
        self.stepStageLabel.setGeometry(QRect(140, 115, 40, 25))
        self.stepStageLabel.setText("Step")

        self.xystage = XYstage()
        
        if self.xystage.xystageInit is False:
            self.enableButtons(False)
            self.stageLabel.setText("XYstage libraries or connection failed")
        else:
            self.stageLabel.setText("XYstage connection OK")

    # Enable/disable buttons and fields
    def enableButtons(self, flag):
        self.homingButton.setEnabled(flag)
        self.setCurPositOriginButton.setEnabled(flag)
        self.upButton.setEnabled(flag)
        self.downButton.setEnabled(flag)
        self.leftButton.setEnabled(flag)
        self.rightButton.setEnabled(flag)
        self.stepStageText.setEnabled(flag)

    # Move stage to home position
    def moveHome(self):
        self.stageLabel.setText("Moving stage to home position...")
        QApplication.processEvents()
        self.xystage.move_home()
        self.stageLabel.setText("Ready")

    # Set current position as origin
    def setCurrentPosOrigin(self):
        self.stageLabel.setText("Setting current position as origin")
        QApplication.processEvents()
        self.xystage.set_origin(True, (_,_))

    # Move stage with buttons.
    # x and y must be either 1, 0, -1
    def moveStage(self,x,y):
        step = float(self.stepStageText.text())
        self.move_rel(x*step, y*step)





