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
    QVBoxLayout,QGridLayout,QLabel,QGraphicsView,QFileDialog,QStatusBar,
    QGraphicsScene,QLineEdit,QMessageBox,QDialog,QDialogButtonBox,QMenuBar)
from PyQt5.QtGui import (QIcon,QImage,QKeySequence,QPixmap,QPainter)
from PyQt5.QtCore import (pyqtSlot,QRectF,QRect)

from .acquisition import *
from . import config


'''
   Acquisition Window
'''
class AcquisitionWindow(QMainWindow):
    def __init__(self):
        super(AcquisitionWindow, self).__init__()
        self.initUI(self)
    
    def initUI(self,MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(772, 707)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayoutWidget = QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QRect(10, 30, 751, 236))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(10, 1, 10, 1)
        self.gridLayout.setHorizontalSpacing(10)
        self.gridLayout.setObjectName("gridLayout")
        self.delayBeforeMeasText = QLineEdit(self.gridLayoutWidget)
        self.delayBeforeMeasText.setObjectName("delayBeforeMeasText")
        self.gridLayout.addWidget(self.delayBeforeMeasText, 5, 1, 1, 1)
        self.minVLabel = QLabel(self.gridLayoutWidget)
        self.minVLabel.setObjectName("minVLabel")
        self.gridLayout.addWidget(self.minVLabel, 0, 0, 1, 1)
        self.minVText = QLineEdit(self.gridLayoutWidget)
        self.minVText.setObjectName("minVText")
        self.gridLayout.addWidget(self.minVText, 0, 1, 1, 1)
        self.numAverScansText = QLineEdit(self.gridLayoutWidget)
        self.numAverScansText.setObjectName("numAverScansText")
        self.gridLayout.addWidget(self.numAverScansText, 4, 1, 1, 1)
        self.numAverScansLabel = QLabel(self.gridLayoutWidget)
        self.numAverScansLabel.setObjectName("numAverScansLabel")
        self.gridLayout.addWidget(self.numAverScansLabel, 4, 0, 1, 1)
        self.startVLabel = QLabel(self.gridLayoutWidget)
        self.startVLabel.setObjectName("startVLabel")
        self.gridLayout.addWidget(self.startVLabel, 2, 0, 1, 1)
        self.startVText = QLineEdit(self.gridLayoutWidget)
        self.startVText.setObjectName("startVText")
        self.gridLayout.addWidget(self.startVText, 2, 1, 1, 1)
        self.stepVLabel = QLabel(self.gridLayoutWidget)
        self.stepVLabel.setObjectName("stepVLabel")
        self.gridLayout.addWidget(self.stepVLabel, 3, 0, 1, 1)
        self.maxVStep = QLineEdit(self.gridLayoutWidget)
        self.maxVStep.setObjectName("maxVStep")
        self.gridLayout.addWidget(self.maxVStep, 1, 1, 1, 1)
        self.maxVLabel = QLabel(self.gridLayoutWidget)
        self.maxVLabel.setObjectName("maxVLabel")
        self.gridLayout.addWidget(self.maxVLabel, 1, 0, 1, 1)
        self.delayBeforeMeasLabel = QLabel(self.gridLayoutWidget)
        self.delayBeforeMeasLabel.setObjectName("delayBeforeMeasLabel")
        self.gridLayout.addWidget(self.delayBeforeMeasLabel, 5, 0, 1, 1)
        self.stepVText = QLineEdit(self.gridLayoutWidget)
        self.stepVText.setObjectName("stepVText")
        self.gridLayout.addWidget(self.stepVText, 3, 1, 1, 1)
        self.steadyStatLabel = QLabel(self.centralwidget)
        self.steadyStatLabel.setGeometry(QRect(20, 10, 111, 16))
        self.steadyStatLabel.setObjectName("steadyStatLabel")
        self.buttonBox = QDialogButtonBox(self.centralwidget)
        self.buttonBox.setGeometry(QRect(590, 630, 164, 32))
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.applyButton = QPushButton(self.centralwidget)
        self.applyButton.setGeometry(QRect(10, 630, 113, 32))
        self.applyButton.setObjectName("applyButton")
        self.trackingLabel = QLabel(self.centralwidget)
        self.trackingLabel.setGeometry(QRect(20, 410, 141, 16))
        self.trackingLabel.setObjectName("trackingLabel")
        self.gridLayoutWidget_2 = QWidget(self.centralwidget)
        self.gridLayoutWidget_2.setGeometry(QRect(10, 430, 751, 181))
        self.gridLayoutWidget_2.setObjectName("gridLayoutWidget_2")
        self.gridLayout_2 = QGridLayout(self.gridLayoutWidget_2)
        self.gridLayout_2.setContentsMargins(10, 1, 10, 1)
        self.gridLayout_2.setHorizontalSpacing(10)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.numPointsText = QLineEdit(self.gridLayoutWidget_2)
        self.numPointsText.setObjectName("numPointsText")
        self.gridLayout_2.addWidget(self.numPointsText, 0, 1, 1, 1)
        self.totTimePerDeviceLabel = QLabel(self.gridLayoutWidget_2)
        self.totTimePerDeviceLabel.setObjectName("totTimePerDeviceLabel")
        self.gridLayout_2.addWidget(self.totTimePerDeviceLabel, 2, 0, 1, 1)
        self.intervalLabel = QLabel(self.gridLayoutWidget_2)
        self.intervalLabel.setObjectName("intervalLabel")
        self.gridLayout_2.addWidget(self.intervalLabel, 1, 0, 1, 1)
        self.IntervalText = QLineEdit(self.gridLayoutWidget_2)
        self.IntervalText.setObjectName("IntervalText")
        self.gridLayout_2.addWidget(self.IntervalText, 1, 1, 1, 1)
        self.numPointsLabel = QLabel(self.gridLayoutWidget_2)
        self.numPointsLabel.setObjectName("numPointsLabel")
        self.gridLayout_2.addWidget(self.numPointsLabel, 0, 0, 1, 1)
        self.totTimePerDeviceText = QLineEdit(self.gridLayoutWidget_2)
        self.totTimePerDeviceText.setObjectName("totTimePerDeviceText")
        self.gridLayout_2.addWidget(self.totTimePerDeviceText, 2, 1, 1, 1)
        self.transientLabel = QLabel(self.centralwidget)
        self.transientLabel.setGeometry(QRect(20, 290, 141, 16))
        self.transientLabel.setObjectName("transientLabel")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setGeometry(QRect(0, 0, 772, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.statusBar().showMessage("Acquisition: Ready", 5000)
        
        MainWindow.setWindowTitle("Acquisition Window")
        self.minVLabel.setText("Min Voltage [V]")
        self.numAverScansLabel.setText("# averaged scans ")
        self.startVLabel.setText("Start Voltage [V]")
        self.stepVLabel.setText("Step Voltage [V]")
        self.maxVLabel.setText("Max Voltage [V]")
        self.delayBeforeMeasLabel.setText("Delays before measurements [sec]")
        self.steadyStatLabel.setText("Steady State")
        self.applyButton.setText("Apply")
        self.trackingLabel.setText("Tracking Voc, JSC, MPP")
        self.totTimePerDeviceLabel.setText("Total time per device")
        self.intervalLabel.setText("Interval")
        self.numPointsLabel.setText("Number of points")
        self.totTimePerDeviceText.setText("Calculated: (Interval+mesurement_time)*#points")
        self.transientLabel.setText("Transient")

