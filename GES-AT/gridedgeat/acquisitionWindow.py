'''
AcquisitionWindow
------------------
Class for providing a graphical user interface for 
Acqusition Window

Copyright (C) 2017 Nicola Ferralis <ferralis@mit.edu>
Copyright (C) 2017 Auto-testing team - MIT GridEdge Solar

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

'''

import sys
from datetime import datetime
from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton, QWidget, QAction,
    QVBoxLayout,QGridLayout,QLabel,QGraphicsView,QFileDialog,QStatusBar,QSpinBox,
    QGraphicsScene,QLineEdit,QMessageBox,QDialog,QDialogButtonBox,QMenuBar)
from PyQt5.QtGui import (QIcon,QImage,QKeySequence,QPixmap,QPainter)
from PyQt5.QtCore import (pyqtSlot,QRectF,QRect)

'''
   Acquisition Window
'''
class AcquisitionWindow(QMainWindow):
    def __init__(self, parent=None):
        super(AcquisitionWindow, self).__init__(parent)
        self.initUI(self)
    
    def initUI(self,MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setGeometry(10, 270, 350, 470)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayoutWidget = QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QRect(10, 30, 330, 236))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(10, 1, 10, 1)
        self.gridLayout.setHorizontalSpacing(10)
        self.gridLayout.setObjectName("gridLayout")
        self.delayBeforeMeasText = QSpinBox(self)
        self.gridLayout.addWidget(self.delayBeforeMeasText, 5, 1, 1, 1)
        self.minVLabel = QLabel(self.gridLayoutWidget)
        self.minVLabel.setObjectName("minVLabel")
        self.gridLayout.addWidget(self.minVLabel, 0, 0, 1, 1)
        self.minVText = QSpinBox(self)
        self.gridLayout.addWidget(self.minVText, 0, 1, 1, 1)
        self.numAverScansText = QSpinBox(self)
        self.gridLayout.addWidget(self.numAverScansText, 4, 1, 1, 1)
        self.numAverScansLabel = QLabel(self.gridLayoutWidget)
        self.numAverScansLabel.setObjectName("numAverScansLabel")
        self.gridLayout.addWidget(self.numAverScansLabel, 4, 0, 1, 1)
        self.startVLabel = QLabel(self.gridLayoutWidget)
        self.startVLabel.setObjectName("startVLabel")
        self.gridLayout.addWidget(self.startVLabel, 2, 0, 1, 1)
        self.startVText = QSpinBox(self)
        self.gridLayout.addWidget(self.startVText, 2, 1, 1, 1)
        self.stepVLabel = QLabel(self.gridLayoutWidget)
        self.stepVLabel.setObjectName("stepVLabel")
        self.gridLayout.addWidget(self.stepVLabel, 3, 0, 1, 1)
        self.maxVText = QSpinBox(self)
        self.gridLayout.addWidget(self.maxVText, 1, 1, 1, 1)
        self.maxVLabel = QLabel(self.gridLayoutWidget)
        self.maxVLabel.setObjectName("maxVLabel")
        self.gridLayout.addWidget(self.maxVLabel, 1, 0, 1, 1)
        self.delayBeforeMeasLabel = QLabel(self.gridLayoutWidget)
        self.delayBeforeMeasLabel.setObjectName("delayBeforeMeasLabel")
        self.gridLayout.addWidget(self.delayBeforeMeasLabel, 5, 0, 1, 1)
        self.stepVText = QLineEdit(self.gridLayoutWidget)
        self.gridLayout.addWidget(self.stepVText, 3, 1, 1, 1)
        self.steadyStatLabel = QLabel(self.centralwidget)
        self.steadyStatLabel.setGeometry(QRect(20, 10, 111, 16))
        self.steadyStatLabel.setObjectName("steadyStatLabel")
        self.trackingLabel = QLabel(self.centralwidget)
        self.trackingLabel.setGeometry(QRect(20, 280, 141, 16))
        self.trackingLabel.setObjectName("trackingLabel")
        self.gridLayoutWidget_2 = QWidget(self.centralwidget)
        self.gridLayoutWidget_2.setGeometry(QRect(10, 300, 340, 181))
        self.gridLayoutWidget_2.setObjectName("gridLayoutWidget_2")
        self.gridLayout_2 = QGridLayout(self.gridLayoutWidget_2)
        self.gridLayout_2.setContentsMargins(10, 1, 10, 1)
        self.gridLayout_2.setHorizontalSpacing(10)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.numPointsText = QSpinBox(self)
        self.gridLayout_2.addWidget(self.numPointsText, 0, 1, 1, 1)
        self.totTimePerDeviceLabel = QLabel(self.gridLayoutWidget_2)
        self.totTimePerDeviceLabel.setObjectName("totTimePerDeviceLabel")
        self.gridLayout_2.addWidget(self.totTimePerDeviceLabel, 2, 0, 1, 1)
        self.intervalLabel = QLabel(self.gridLayoutWidget_2)
        self.intervalLabel.setObjectName("intervalLabel")
        self.gridLayout_2.addWidget(self.intervalLabel, 1, 0, 1, 1)
        self.IntervalText = QSpinBox(self)
        self.IntervalText.setObjectName("IntervalText")
        self.gridLayout_2.addWidget(self.IntervalText, 1, 1, 1, 1)
        self.numPointsLabel = QLabel(self.gridLayoutWidget_2)
        self.numPointsLabel.setObjectName("numPointsLabel")
        self.gridLayout_2.addWidget(self.numPointsLabel, 0, 0, 1, 1)
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
        self.minVLabel.setText("Min Voltage [V]")
        self.numAverScansLabel.setText("Number of averaged scans ")
        self.startVLabel.setText("Start Voltage [V]")
        self.stepVLabel.setText("Step Voltage [V]")
        self.maxVLabel.setText("Max Voltage [V]")
        self.delayBeforeMeasLabel.setText("Delays before measurements [sec]")
        self.steadyStatLabel.setText("<qt><b>Steady State</b></qt>")
        self.trackingLabel.setText("<qt><b>Tracking Voc, JSC, MPP</b></qt>")
        self.totTimePerDeviceLabel.setText("Total time per device")
        self.intervalLabel.setText("Interval")
        self.numPointsLabel.setText("Number of points")
        self.saveButton = QPushButton(self.centralwidget)
        self.saveButton.setGeometry(QRect(270, 380, 80, 60))
        self.saveButton.setText("Save")
        self.saveButton.clicked.connect(self.saveParameters)
        
        self.defaultButton = QPushButton(self.centralwidget)
        self.defaultButton.setGeometry(QRect(190, 380, 80, 60))
        self.defaultButton.setText("Default")
        self.defaultButton.clicked.connect(self.defaultParameters)
        
        self.initParameters()

    def saveParameters(self):
        self.parent().config.conf['Acquisition']['acqMinVoltage'] = str(self.minVText.value())
        self.parent().config.conf['Acquisition']['acqMaxVoltage'] = str(self.maxVText.value())
        self.parent().config.conf['Acquisition']['acqStartVoltage'] = str(self.startVText.value())
        self.parent().config.conf['Acquisition']['acqStepVoltage'] = str(self.stepVText.text())
        self.parent().config.conf['Acquisition']['acqNumAvScans'] = str(self.numAverScansText.value())
        self.parent().config.conf['Acquisition']['acqDelBeforeMeas'] = str(self.delayBeforeMeasText.value())
        self.parent().config.conf['Acquisition']['acqTrackNumPoints'] = str(self.numPointsText.value())
        self.parent().config.conf['Acquisition']['acqTrackInterval'] = str(self.IntervalText.value())
        with open(self.parent().config.configFile, 'w') as configfile:
            self.parent().config.conf.write(configfile)
        print("Save parameters as default")
        self.timePerDevice()
    
    def defaultParameters(self):
        self.parent().config.createConfig()
        self.initParameters()
        print("Restored default parameters")
        self.timePerDevice()

    def initParameters(self):
        self.minVText.setValue(float(self.parent().config.acqMinVoltage))
        self.maxVText.setValue(float(self.parent().config.acqMaxVoltage))
        self.startVText.setValue(float(self.parent().config.acqStartVoltage))
        self.stepVText.setText(str(self.parent().config.acqStepVoltage))
        self.numAverScansText.setValue(float(self.parent().config.acqNumAvScans))
        self.delayBeforeMeasText.setValue(float(self.parent().config.acqDelBeforeMeas))
        self.numPointsText.setValue(int(self.parent().config.acqTrackNumPoints))
        self.IntervalText.setValue(float(self.parent().config.acqTrackInterval))
        self.timePerDevice()

    def timePerDevice(self):
        timePerDevice = (int(self.parent().config.acqNumAvScans) * (0.1+float(self.parent().config.acqDelBeforeMeas)) + float(self.parent().config.acqTrackInterval)) * int(self.parent().config.acqTrackNumPoints)
        self.totTimePerDeviceLabel.setText("Total time per device: <qt><b>{0:0.1f}s</b></qt>".format(timePerDevice))

    # Enable and disable fields (flag is either True or False) during acquisition.
    def enableAcqPanel(self, flag):
        self.minVText.setEnabled(flag)
        self.maxVText.setEnabled(flag)
        self.startVText.setEnabled(flag)
        self.stepVText.setEnabled(flag)
        self.numAverScansText.setEnabled(flag)
        self.delayBeforeMeasText.setEnabled(flag)
        self.numPointsText.setEnabled(flag)
        self.IntervalText.setEnabled(flag)
        self.saveButton.setEnabled(flag)
        self.defaultButton.setEnabled(flag)




