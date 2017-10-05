'''
AcquisitionWindow
------------------
Class for providing a graphical user interface for 
Acqusition Window

Copyright (C) 2017 Nicola Ferralis <ferralis@mit.edu>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

'''
import sys
import numpy as np
from datetime import datetime
from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton, QWidget, QAction,
    QVBoxLayout,QGridLayout,QLabel,QGraphicsView,QFileDialog,QStatusBar,QSpinBox,
    QGraphicsScene,QLineEdit,QMessageBox,QDialog,QDialogButtonBox,QMenuBar,QComboBox)
from PyQt5.QtGui import (QIcon,QImage,QKeySequence,QPixmap,QPainter,QDoubleValidator)
from PyQt5.QtCore import (pyqtSlot,QRectF,QRect)

from . import logger

'''
   Acquisition Window
'''
class AcquisitionWindow(QMainWindow):
    def __init__(self, parent=None):
        super(AcquisitionWindow, self).__init__(parent)
        self.initUI(self)
    
    # Setup UI elements
    def initUI(self,MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setGeometry(10, 290, 340, 520)
        self.setFixedSize(self.size())
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayoutWidget = QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QRect(10, 30, 330, 260))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setHorizontalSpacing(10)
        self.gridLayout.setObjectName("gridLayout")
        self.steadyStatLabel = QLabel(self.centralwidget)
        self.steadyStatLabel.setGeometry(QRect(10, 10, 111, 16))
        
        self.soakVLabel = QLabel(self.gridLayoutWidget)
        self.gridLayout.addWidget(self.soakVLabel, 0, 0, 1, 1)
        self.soakVText = QLineEdit(self)
        self.gridLayout.addWidget(self.soakVText, 0, 1, 1, 1)

        self.soakTLabel = QLabel(self.gridLayoutWidget)
        self.gridLayout.addWidget(self.soakTLabel, 1, 0, 1, 1)
        self.soakTText = QLineEdit(self)
        self.gridLayout.addWidget(self.soakTText, 1, 1, 1, 1)
        
        self.holdTLabel = QLabel(self.gridLayoutWidget)
        self.gridLayout.addWidget(self.holdTLabel, 2, 0, 1, 1)
        self.holdTText = QLineEdit(self)
        self.gridLayout.addWidget(self.holdTText, 2, 1, 1, 1)
        
        self.forwardVLabel = QLabel(self.gridLayoutWidget)
        self.gridLayout.addWidget(self.forwardVLabel, 3, 0, 1, 1)
        self.forwardVText = QLineEdit(self)
        self.gridLayout.addWidget(self.forwardVText, 3, 1, 1, 1)
        
        self.reverseVLabel = QLabel(self.gridLayoutWidget)
        self.gridLayout.addWidget(self.reverseVLabel, 4, 0, 1, 1)
        self.reverseVText = QLineEdit(self)
        self.gridLayout.addWidget(self.reverseVText, 4, 1, 1, 1)

        self.stepVLabel = QLabel(self.gridLayoutWidget)
        self.gridLayout.addWidget(self.stepVLabel, 5, 0, 1, 1)
        self.stepVText = QLineEdit(self.gridLayoutWidget)
        self.gridLayout.addWidget(self.stepVText, 5, 1, 1, 1)
        
        self.directionLabel = QLabel(self.gridLayoutWidget)
        self.gridLayout.addWidget(self.directionLabel, 6, 0, 1, 1)
        self.directionCBox = QComboBox(self)
        self.gridLayout.addWidget(self.directionCBox, 6, 1, 1, 1)
        self.directionCBox.addItem("Vr \u2192 Vf")
        self.directionCBox.addItem("Vf \u2192 Vr")

        self.reverseVText.textEdited.connect(self.validateReverseVoltage)
        self.forwardVText.textEdited.connect(self.validateForwardVoltage)
        
        self.architectureLabel = QLabel(self.gridLayoutWidget)
        self.gridLayout.addWidget(self.architectureLabel, 7, 0, 1, 1)
        self.architectureCBox = QComboBox(self)
        self.gridLayout.addWidget(self.architectureCBox, 7, 1, 1, 1)
        self.architectureCBox.addItem("NP")
        self.architectureCBox.addItem("PN")
        
        self.delayBeforeMeasLabel = QLabel(self.gridLayoutWidget)
        self.gridLayout.addWidget(self.delayBeforeMeasLabel, 8, 0, 1, 1)
        self.delayBeforeMeasText = QLineEdit(self)
        self.gridLayout.addWidget(self.delayBeforeMeasText, 8, 1, 1, 1)
        
        self.trackingLabel = QLabel(self.centralwidget)
        self.trackingLabel.setGeometry(QRect(10, 300, 160, 16))
        self.trackingLabel.setObjectName("trackingLabel")
        
        self.gridLayoutWidget_2 = QWidget(self.centralwidget)
        self.gridLayoutWidget_2.setGeometry(QRect(10, 320, 330, 181))
        self.gridLayoutWidget_2.setObjectName("gridLayoutWidget_2")
        self.gridLayout_2 = QGridLayout(self.gridLayoutWidget_2)
        self.gridLayout_2.setHorizontalSpacing(10)
        self.gridLayout_2.setObjectName("gridLayout_2")

        self.numDevTrackLabel = QLabel(self.gridLayoutWidget_2)
        self.gridLayout_2.addWidget(self.numDevTrackLabel, 0, 0, 1, 1)
        self.numDevTrackText = QSpinBox(self)
        self.gridLayout_2.addWidget(self.numDevTrackText, 0, 1, 1, 1)
        
        self.trackTLabel = QLabel(self.gridLayoutWidget_2)
        self.gridLayout_2.addWidget(self.trackTLabel, 1, 0, 1, 1)
        self.trackTText = QLineEdit(self)
        self.gridLayout_2.addWidget(self.trackTText, 1, 1, 1, 1)
        
        self.totTimePerDeviceLabel = QLabel(self.gridLayoutWidget_2)
        self.gridLayout_2.addWidget(self.totTimePerDeviceLabel, 2, 0, 1, 1)
       
        MainWindow.setCentralWidget(self.centralwidget)
        
        self.menuBar = QMenuBar(MainWindow)
        self.menuBar.setGeometry(QRect(0, 0, 772, 22))
        self.menuBar.setObjectName("menubar")
        
        self.parent().viewWindowMenus(self.menuBar, self.parent())
        
        MainWindow.setMenuBar(self.menuBar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.statusBar().showMessage("Acquisition: Ready", 5000)
        
        MainWindow.setWindowTitle("Acquisition Window")
        self.steadyStatLabel.setText("<qt><b>Steady State</b></qt>")
        self.soakVLabel.setText("Soak voltage [V]")
        self.soakTLabel.setText("Soak time [s]")
        self.holdTLabel.setText("Hold time [s]")
        self.forwardVLabel.setText("Forward voltage [V]")
        self.reverseVLabel.setText("Reverse voltage [V]")
        self.stepVLabel.setText("Step voltage [V]")
        self.directionLabel.setText("Scan direction: ")
        self.architectureLabel.setText("Device architecture: ")
        self.delayBeforeMeasLabel.setText("Delays before measurements [s]")
        self.trackingLabel.setText("<qt><b>Track MPP: </b></qt>")
        self.numDevTrackLabel.setText("Number of devices to be tracked")
        self.trackTLabel.setText("Tracking time [s]")

        self.saveButton = QPushButton(self.centralwidget)
        self.saveButton.setGeometry(QRect(250, 410, 80, 60))
        self.saveButton.setText("Save")
        self.saveButton.clicked.connect(self.saveParameters)
        
        self.defaultButton = QPushButton(self.centralwidget)
        self.defaultButton.setGeometry(QRect(160, 410, 80, 60))
        self.defaultButton.setText("Default")
        self.defaultButton.clicked.connect(self.defaultParameters)
        
        self.initParameters()
    
        self.soakTText.editingFinished.connect(self.timePerDevice)
        self.forwardVText.editingFinished.connect(self.timePerDevice)
        self.reverseVText.editingFinished.connect(self.timePerDevice)
        self.stepVText.editingFinished.connect(self.timePerDevice)
        self.delayBeforeMeasText.editingFinished.connect(self.timePerDevice)

    # Save acquisition parameters in configuration ini
    def saveParameters(self):
        self.parent().config.conf['Acquisition']['acqSoakVoltage'] = str(self.soakVText.text())
        self.parent().config.conf['Acquisition']['acqSoakTime'] = str(self.soakTText.text())
        self.parent().config.conf['Acquisition']['acqHoldTime'] = str(self.holdTText.text())
        self.parent().config.conf['Acquisition']['acqStepVoltage'] = str(self.stepVText.text())
        self.parent().config.conf['Acquisition']['acqForwardVoltage'] = str(self.forwardVText.text())
        self.parent().config.conf['Acquisition']['acqReverseVoltage'] = str(self.reverseVText.text())
        self.parent().config.conf['Acquisition']['acqDelayBeforeMeas'] = str(self.delayBeforeMeasText.text())
        self.parent().config.conf['Acquisition']['acqDirection'] = str(self.directionCBox.currentIndex())
        self.parent().config.conf['Acquisition']['acqArchitecture'] = str(self.architectureCBox.currentIndex())
        self.parent().config.conf['Acquisition']['acqTrackNumDevices'] = str(self.numDevTrackText.value())
        self.parent().config.conf['Acquisition']['acqTrackTime'] = str(self.trackTText.text())

        self.parent().config.saveConfig(self.parent().config.configFile)
        self.parent().config.readConfig(self.parent().config.configFile)
        print("Acquisition parameters saved as default")
        logger.info("Acquisition parameters saved as default")
        self.timePerDevice()
    
    # Set default acquisition parameters from configuration ini
    def defaultParameters(self):
        self.parent().config.createConfig()
        self.parent().config.readConfig(self.parent().config.configFile)
        self.initParameters()
        print("Default acquisition parameters restored")
        logger.info("Default acquisition parameters restored")
        self.timePerDevice()

    # Populate acquisition panel with values from config
    def initParameters(self):
        self.soakVText.setText(str(self.parent().config.acqSoakVoltage))
        self.soakTText.setText(str(self.parent().config.acqSoakTime))
        self.holdTText.setText(str(self.parent().config.acqHoldTime))
        self.stepVText.setText(str(self.parent().config.acqStepVoltage))
        self.reverseVText.setText(str(self.parent().config.acqReverseVoltage))
        self.forwardVText.setText(str(self.parent().config.acqForwardVoltage))
        self.directionCBox.setCurrentIndex(int(self.parent().config.acqDirection))
        self.architectureCBox.setCurrentIndex(int(self.parent().config.acqArchitecture))
        self.delayBeforeMeasText.setText(str(self.parent().config.acqDelayBeforeMeas))
        self.numDevTrackText.setValue(int(self.parent().config.acqTrackNumDevices))
        self.trackTText.setText(str(self.parent().config.acqTrackTime))
        self.timePerDevice()

    # Field validator for Reverse and Forward Voltages
    def validateReverseVoltage(self):
        validateVoltage = QDoubleValidator(-50, float(self.forwardVText.text()),1,self.reverseVText)
        if validateVoltage.validate(self.reverseVText.text(),1)[0] != 2:
            msg = "Reverse voltage needs to be less than\n forward voltage (V_f="+self.forwardVText.text()+\
                  ")\n\nPlease change \"Reverse voltage\" in the Acquisition window"
            reply = QMessageBox.question(self, 'Critical', msg, QMessageBox.Ok)
            self.show()
            
    def validateForwardVoltage(self):
        validateVoltage = QDoubleValidator(float(self.reverseVText.text()),50,1,self.forwardVText)
        if validateVoltage.validate(self.forwardVText.text(),1)[0] != 2:
            msg = "Forward voltage needs to be more than\n reverse voltage (V_r="+self.reverseVText.text()+\
                  ")\n\nPlease change \"Forward voltage\" in the Acquisition window"
            reply = QMessageBox.question(self, 'Critical', msg, QMessageBox.Ok)
            self.show()  

    # Calculate the measurement time per device
    def timePerDevice(self):
        try:
            timePerDevice = len(np.arange(float(self.reverseVText.text())-1e-9,
                                      float(self.forwardVText.text())+1e-9,
                                      float(self.stepVText.text())))* \
                                      float(self.holdTText.text()) + \
                                      float(self.soakTText.text())
        except:
            timePerDevice = 0
        self.totTimePerDeviceLabel.setText(\
                "Total time per device: <qt><b>{0:0.1f}s</b></qt>".format(timePerDevice))
    

    # Enable and disable fields (flag is either True or False) during acquisition.
    def enableAcqPanel(self, flag):
        self.soakVText.setEnabled(flag)
        self.soakTText.setEnabled(flag)
        self.holdTText.setEnabled(flag)
        self.stepVText.setEnabled(flag)
        self.forwardVText.setEnabled(flag)
        self.reverseVText.setEnabled(flag)
        self.architectureCBox.setEnabled(flag)
        self.directionCBox.setEnabled(flag)
        self.delayBeforeMeasText.setEnabled(flag)
        self.trackTText.setEnabled(flag)
        self.numDevTrackText.setEnabled(flag)
        self.saveButton.setEnabled(flag)
        self.defaultButton.setEnabled(flag)
