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
        self.setGeometry(20, 200, 310, 250)
        StageWindow.setWindowTitle("XY stage control settings")

        self.stageLabel = QLabel(StageWindow)
        self.stageLabel.setGeometry(QRect(20, 20, 300, 20))

        self.homingButton = QPushButton(StageWindow)
        self.homingButton.setGeometry(QRect(10, 65, 100, 30))
        self.homingButton.setText("Move Home")
        self.homingButton.clicked.connect(self.moveHome)
        
        self.setCurPositOriginButton = QPushButton(StageWindow)
        self.setCurPositOriginButton.setGeometry(QRect(190, 65, 100, 30))
        self.setCurPositOriginButton.setText("Set Origin")
        self.setCurPositOriginButton.clicked.connect(self.setCurrentPosOrigin)
        
        self.upButton = QPushButton(StageWindow)
        self.upButton.setGeometry(QRect(120, 50, 60, 60))
        self.upButton.setText("UP")
        self.upButton.clicked.connect(lambda: self.moveStageRel(0,1))
        self.downButton = QPushButton(StageWindow)
        self.downButton.setGeometry(QRect(120, 170, 60, 60))
        self.downButton.setText("DOWN")
        self.downButton.clicked.connect(lambda: self.moveStageRel(0,-1))
        self.leftButton = QPushButton(StageWindow)
        self.leftButton.setGeometry(QRect(50, 110, 60, 60))
        self.leftButton.setText("LEFT")
        self.leftButton.clicked.connect(lambda: self.moveStageRel(-1,0))
        self.rightButton = QPushButton(StageWindow)
        self.rightButton.setGeometry(QRect(190, 110, 60, 60))
        self.rightButton.setText("RIGHT")
        self.rightButton.clicked.connect(lambda: self.moveStageRel(1,0))
        
        self.stepStageText = QLineEdit(StageWindow)
        self.stepStageText.setGeometry(QRect(135, 140, 40, 25))
        self.stepStageText.setText("1")
        self.stepStageLabel = QLabel(StageWindow)
        self.stepStageLabel.setGeometry(QRect(140, 115, 40, 25))
        self.stepStageLabel.setText("Step")
        
        self.xPosStageText = QLineEdit(StageWindow)
        self.xPosStageText.setGeometry(QRect(70, 180, 40, 25))
        self.yPosStageText = QLineEdit(StageWindow)
        self.yPosStageText.setGeometry(QRect(70, 210, 40, 25))
        self.goToButton = QPushButton(StageWindow)
        self.goToButton.setGeometry(QRect(5, 177, 60, 60))
        self.goToButton.setText("Go X\nGo Y")
        self.goToButton.clicked.connect(self.moveStageAbs)

        self.subPosStageText = QLineEdit(StageWindow)
        self.subPosStageText.setGeometry(QRect(260, 190, 40, 25))
        self.subPosStageText.setText("1")

        self.subToButton = QPushButton(StageWindow)
        self.subToButton.setGeometry(QRect(190, 177, 60, 60))
        self.subToButton.setText("Go\n Subs")
        self.subToButton.clicked.connect(self.moveToSubstrate)
        
        self.xystage = XYstage()
        
        if self.xystage.xystageInit is False:
            self.enableButtons(False)
            self.stageLabel.setText("XYstage libraries or connection failed")
        else:
            self.showCurrentPos()

    # Enable/disable buttons and fields
    def enableButtons(self, flag):
        self.homingButton.setEnabled(flag)
        self.setCurPositOriginButton.setEnabled(flag)
        self.upButton.setEnabled(flag)
        self.downButton.setEnabled(flag)
        self.leftButton.setEnabled(flag)
        self.rightButton.setEnabled(flag)
        self.stepStageText.setEnabled(flag)
        self.xPosStageText.setEnabled(flag)
        self.yPosStageText.setEnabled(flag)
        self.goToButton.setEnabled(flag)
        self.subPosStageText.setEnabled(flag)
        self.subToButton.setEnabled(flag)

    # Move stage to home position
    def moveHome(self):
        self.stageLabel.setText("Moving stage to home position...")
        QApplication.processEvents()
        self.xystage.move_home()
        self.showCurrentPos()
        
    # Set current position as origin
    def setCurrentPosOrigin(self):
        self.stageLabel.setText("Setting current position as origin")
        QApplication.processEvents()
        self.xystage.set_origin(True, (_,_))
        QApplication.processEvents()
        self.showCurrentPos()

    # Move stage with buttons.
    # x and y must be either 1, 0, -1
    def moveStageRel(self,x,y):
        step = float(self.stepStageText.text())
        self.xystage.move_rel(x*step, y*step)
        self.showCurrentPos()
    
    # Move stage to location set in the LineEdits.
    def moveStageAbs(self):
        self.xystage.move_abs(float(self.xPosStageText.text()),
            float(self.yPosStageText.text()))
        self.showCurrentPos()

    # Get and show current stage position
    def showCurrentPos(self):
        currPos = ["{0:0.2f}".format(float(self.xystage.get_curr_pos()[0])),
                    "{0:0.2f}".format(float(self.xystage.get_curr_pos()[1]))]
        self.xPosStageText.setText(currPos[0])
        self.yPosStageText.setText(currPos[1])
        msg = "Stage current position: ("+currPos[0]+", "+currPos[1]+")"
        self.stageLabel.setText(msg)
        print(msg)

    # Move stage to location set in the LineEdits.
    def moveToSubstrate(self):
        sub = int(self.subPosStageText.text())
        self.xystage.move_to_substrate_4x4(sub)
        self.showCurrentPos()







