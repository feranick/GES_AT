'''
stageWindow
------------------
Class for providing a graphical user interface for 
XY stage panel

Copyright (C) 2017 Nicola Ferralis <ferralis@mit.edu>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

'''
from PyQt5.QtCore import QRect
from PyQt5.QtWidgets import (QLabel, QLineEdit, QPushButton, QWidget,
                             QMainWindow, QApplication)
from PyQt5.QtGui import (QIntValidator)
from .modules.xystage.xystage import *
from .acquisition import *

class StageWindow(QMainWindow):
    def __init__(self, parent=None):
        super(StageWindow, self).__init__(parent)
        self.initUI(self)
        self.activeStage = False
    
    # Setup UI elements
    def initUI(self, StageWindow):
        self.setGeometry(400, 30, 310, 400)
        StageWindow.setWindowTitle("XY stage control settings")
        self.setFixedSize(self.size())
        
        self.homingButton = QPushButton(StageWindow)
        self.homingButton.setGeometry(QRect(10, 30, 100, 30))
        self.homingButton.setText("Move Home")
        self.homingButton.clicked.connect(self.moveHome)
        
        self.setCurPositOriginButton = QPushButton(StageWindow)
        self.setCurPositOriginButton.setGeometry(QRect(190, 30, 100, 30))
        self.setCurPositOriginButton.setText("Set Origin")
        self.setCurPositOriginButton.clicked.connect(self.setCurrentPosOrigin)
        
        self.upButton = QPushButton(StageWindow)
        self.upButton.setGeometry(QRect(120, 20, 60, 60))
        self.upButton.setText("+X")
        self.upButton.setShortcut("up")
        self.upButton.clicked.connect(lambda: self.moveStageRel(1,0))
        self.downButton = QPushButton(StageWindow)
        self.downButton.setGeometry(QRect(120, 140, 60, 60))
        self.downButton.setText("-X")
        self.downButton.setShortcut("down")
        self.downButton.clicked.connect(lambda: self.moveStageRel(-1,0))
        self.leftButton = QPushButton(StageWindow)
        self.leftButton.setGeometry(QRect(50, 80, 60, 60))
        self.leftButton.setText("-Y")
        self.leftButton.setShortcut("left")
        self.leftButton.clicked.connect(lambda: self.moveStageRel(0,-1))
        self.rightButton = QPushButton(StageWindow)
        self.rightButton.setGeometry(QRect(190, 80, 60, 60))
        self.rightButton.setText("+Y")
        self.rightButton.setShortcut("right")
        self.rightButton.clicked.connect(lambda: self.moveStageRel(0,1))
        
        self.stepStageText = QLineEdit(StageWindow)
        self.stepStageText.setGeometry(QRect(130, 100, 40, 25))
        self.stepStageText.setText("1")
        self.stepStageLabel = QLabel(StageWindow)
        self.stepStageLabel.setGeometry(QRect(130, 75, 40, 25))
        self.stepStageLabel.setText("Step")
        
        self.xPosStageText = QLineEdit(StageWindow)
        self.xPosStageText.setGeometry(QRect(15, 180, 40, 25))
        self.yPosStageText = QLineEdit(StageWindow)
        self.yPosStageText.setGeometry(QRect(65, 180, 40, 25))
        self.goToButton = QPushButton(StageWindow)
        self.goToButton.setGeometry(QRect(10, 150, 100, 30))
        self.goToButton.setText("Go XY")
        self.goToButton.clicked.connect(self.moveStageAbs)

        self.subPosStageText = QLineEdit(StageWindow)
        self.subPosStageText.setGeometry(QRect(190, 180, 50, 25))
        self.subPosStageText.setText("2")
        self.devPosStageText = QLineEdit(StageWindow)
        self.devPosStageText.setGeometry(QRect(250, 180, 50, 25))
        self.devPosStageText.setText("1")

        self.subToButton = QPushButton(StageWindow)
        self.subToButton.setGeometry(QRect(180, 150, 130, 30))
        self.subToButton.setText("Substrate/Device")
        self.subToButton.clicked.connect(self.moveToSubstrate)
        
        self.stageLabel = QLabel(StageWindow)
        self.stageLabel.setGeometry(QRect(20, 220, 300, 20))
        
        self.activateStageButton = QPushButton(StageWindow)
        self.activateStageButton.setGeometry(QRect(10, 250, 290, 40))
        self.activateStageButton.setText("Activate Stage")
        self.activateStageButton.clicked.connect(self.activateStage)
        
        self.moveToPowermeterButton = QPushButton(StageWindow)
        self.moveToPowermeterButton.setGeometry(QRect(10, 300, 290, 40))
        self.moveToPowermeterButton.setText("Move to Powermeter")
        self.moveToPowermeterButton.clicked.connect(self.moveToPowermeter)
        self.moveToPowermeterButton.setEnabled(False)
        
        self.moveToReferenceCellButton = QPushButton(StageWindow)
        self.moveToReferenceCellButton.setGeometry(QRect(10, 350, 290, 40))
        self.moveToReferenceCellButton.setText("Move to Reference Cell")
        self.moveToReferenceCellButton.clicked.connect(self.moveToReferenceCell)
        self.moveToReferenceCellButton.setEnabled(False)
        
        self.enableButtons(False)
    
    # Logic for activating the stage
    def activateStage(self):
        if self.activeStage == False:
            self.activateStageButton.setEnabled(False)
            self.stageLabel.setText("Activating XY stage...")
            QApplication.processEvents()
            self.xystage = XYstage()
            if self.xystage.xystageInit is False:
                self.enableButtons(False)
                self.stageLabel.setText("XY stage libraries or connection failed")
                self.activateStageButton.setEnabled(False)
            else:
                self.activateStageButton.setEnabled(True)
                self.activateStageButton.setText("Deactivate Stage")
                self.activeStage = True
                self.enableButtons(True)
                self.showCurrentPos()
        else:
            self.stageLabel.setText("Deactivating XY stage...")
            QApplication.processEvents()
            print(" Moving to position [5,5]")
            self.xystage.move_abs(5,5)
            if self.xystage.xystageInit is True:
                self.xystage.end_stage_control()
                del self.xystage
            self.activateStageButton.setText("Activate Stage")
            self.enableButtons(False)
            self.stageLabel.setText("XY stage deactivated")
            self.activeStage = False
            print(" XY stage deactivated")
            
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
        self.devPosStageText.setEnabled(flag)
        self.subToButton.setEnabled(flag)
        self.moveToReferenceCellButton.setEnabled(flag)
        self.moveToPowermeterButton.setEnabled(flag)


    # Move stage to home position
    def moveHome(self):
        self.stageLabel.setText("Moving stage to home position...")
        QApplication.processEvents()
        self.xystage.move_home(True)
        self.showCurrentPos()
    
    # Move stage to position of reference solar cell
    def moveToReferenceCell(self):
        self.stageLabel.setText("Moving stage to Reference Cell...")
        QApplication.processEvents()
        self.xystage.move_abs(float(self.parent().config.xPosRefCell),
                              float(self.parent().config.yPosRefCell))
        self.showCurrentPos()
    
    # Move stage to position of reference solar cell
    def moveToReferenceCell(self):
        self.stageLabel.setText("Moving stage to Reference Cell...")
        #self.parent().config.xPosRefCell
        QApplication.processEvents()
        self.xystage.move_abs(float(self.parent().config.xPosRefCell),
                              float(self.parent().config.yPosRefCell))
        self.showCurrentPos()
    
    # Move stage to position of Powermeter
    def moveToPowermeter(self):
        self.stageLabel.setText("Moving stage to Powermeter...")
        #self.parent().config.xPosRefCell
        QApplication.processEvents()
        self.xystage.move_abs(float(self.parent().config.xPosPowermeter),
                              float(self.parent().config.yPosPowermeter))
        self.showCurrentPos()
        
    # Set current position as origin
    def setCurrentPosOrigin(self):
        self.stageLabel.setText("Setting current position as origin")
        QApplication.processEvents()
        self.xystage.set_origin(True, (0,0))
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
        msg = " Stage current position: ("+currPos[0]+", "+currPos[1]+")"
        self.stageLabel.setText(msg)
        print(msg)

    # Move stage to location set in the LineEdits.
    def moveToSubstrate(self):
        validSubNum = QIntValidator(1,16,self.subPosStageText)
        validDevNum = QIntValidator(0,6,self.devPosStageText)
        if validDevNum.validate(self.devPosStageText.text(),1)[0] == 2 \
           and validSubNum.validate(self.subPosStageText.text(),1)[0] == 2:
            self.xystage.move_to_substrate_4x4(int(self.subPosStageText.text()))
            time.sleep(0.5)
            if int(self.devPosStageText.text()) !=0:
                self.xystage.move_to_device_3x2(int(self.subPosStageText.text()),
                                        int(self.devPosStageText.text()))
                msg = " Substrate #"+self.subPosStageText.text()+\
                                " - Device #"+self.devPosStageText.text()
            else:
                msg = " Substrate #"+self.subPosStageText.text()+" - Center"
            self.showCurrentPos()
        else:
            msg = " Substrates/device indices out of range"
        
        self.stageLabel.setText(msg)
        print(msg)
    '''
    # Move stage to substrate location set by coordinates in the LineEdits.
    def moveToSubstrateCoord(self):
        validXCoord = QIntValidator(1,4,self.subXPosStageText)
        validYCoord = QIntValidator(1,4,self.subYPosStageText)
        validDevNum = QIntValidator(1,6,self.devPosStageText)

        if validDevNum.validate(self.devPosStageText.text(),1)[0] == 2 \
           and validXCoord.validate(self.subXPosStageText.text(),1)[0] == 2 \
           and validYCoord.validate(self.subYPosStageText.text(),1)[0] == 2:
            xCoord = int(self.subXPosStageText.text())-1
            yCoord = int(self.subYPosStageText.text())-1
            ac = Acquisition()
            self.xystage.move_to_substrate_4x4(ac.getSubstrateNumber(xCoord,
                                                                     yCoord))
            time.sleep(0.5)
            devNum = int(self.devPosStageText.text())
            self.xystage.move_to_device_3x2(ac.getSubstrateNumber(xCoord,
                                yCoord),int(self.devPosStageText.text()))
            self.showCurrentPos()
            print("Substrate number:",ac.getSubstrateNumber(xCoord,yCoord))
            del ac
        else:
            msg = "Substrates/device indeces out of range"
            self.stageLabel.setText(msg)
            print(msg)
    '''
    # Close connection upon closing window.
    def closeEvent(self, event):
        if self.activeStage == True:
            self.activateStage()
