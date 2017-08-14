'''
SampleWindow
------------------
Class for providing a graphical user interface for 
Sample Window

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
    QGraphicsScene,QLineEdit,QMessageBox,QDialog,QComboBox,QMenuBar,QDialogButtonBox)
from PyQt5.QtGui import (QIcon,QImage,QKeySequence,QPixmap,QPainter)
from PyQt5.QtCore import (pyqtSlot,QRectF,QRect,QMetaObject,QCoreApplication)

from . import config

'''
   Sample Window
'''
class SampleWindow(QMainWindow):
    def __init__(self):
        super(SampleWindow, self).__init__()
        self.initUI(self)
    
    def initUI(self,MainWindow):
        MainWindow.resize(789, 632)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayoutWidget = QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QRect(10, 10, 751, 531))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.windowGridLayout = QGridLayout(self.gridLayoutWidget)
        self.windowGridLayout.setContentsMargins(0, 0, 0, 0)
        self.windowGridLayout.setObjectName("windowGridLayout")
        self.devLabel = QLabel(self.gridLayoutWidget)
        self.devLabel.setObjectName("devLabel")
        self.windowGridLayout.addWidget(self.devLabel, 3, 0, 1, 1)
        self.devGridLayout = QGridLayout()
        self.devGridLayout.setObjectName("devGridLayout")
        self.devA1Text = QLineEdit(self.gridLayoutWidget)
        self.devA1Text.setObjectName("devA1Text")
        self.devGridLayout.addWidget(self.devA1Text, 0, 0, 1, 1)
        self.devB1Text = QLineEdit(self.gridLayoutWidget)
        self.devB1Text.setObjectName("devB1Text")
        self.devGridLayout.addWidget(self.devB1Text, 1, 0, 1, 1)
        self.devC1Text = QLineEdit(self.gridLayoutWidget)
        self.devC1Text.setObjectName("devC1Text")
        self.devGridLayout.addWidget(self.devC1Text, 2, 0, 1, 1)
        self.devD1Text = QLineEdit(self.gridLayoutWidget)
        self.devD1Text.setObjectName("devD1Text")
        self.devGridLayout.addWidget(self.devD1Text, 3, 0, 1, 1)
        self.devA2Text = QLineEdit(self.gridLayoutWidget)
        self.devA2Text.setObjectName("devA2Text")
        self.devGridLayout.addWidget(self.devA2Text, 0, 1, 1, 1)
        self.devA3Text = QLineEdit(self.gridLayoutWidget)
        self.devA3Text.setObjectName("devA3Text")
        self.devGridLayout.addWidget(self.devA3Text, 0, 2, 1, 1)
        self.devA4Text = QLineEdit(self.gridLayoutWidget)
        self.devA4Text.setObjectName("devA4Text")
        self.devGridLayout.addWidget(self.devA4Text, 0, 3, 1, 1)
        self.devB2Text = QLineEdit(self.gridLayoutWidget)
        self.devB2Text.setObjectName("devB2Text")
        self.devGridLayout.addWidget(self.devB2Text, 1, 1, 1, 1)
        self.devB3Text = QLineEdit(self.gridLayoutWidget)
        self.devB3Text.setObjectName("devB3Text")
        self.devGridLayout.addWidget(self.devB3Text, 1, 2, 1, 1)
        self.devB4Text = QLineEdit(self.gridLayoutWidget)
        self.devB4Text.setObjectName("devB4Text")
        self.devGridLayout.addWidget(self.devB4Text, 1, 3, 1, 1)
        self.devC2Text = QLineEdit(self.gridLayoutWidget)
        self.devC2Text.setObjectName("devC2Text")
        self.devGridLayout.addWidget(self.devC2Text, 2, 1, 1, 1)
        self.devC3Text = QLineEdit(self.gridLayoutWidget)
        self.devC3Text.setObjectName("devC3Text")
        self.devGridLayout.addWidget(self.devC3Text, 2, 2, 1, 1)
        self.devC4Text = QLineEdit(self.gridLayoutWidget)
        self.devC4Text.setObjectName("devC4Text")
        self.devGridLayout.addWidget(self.devC4Text, 2, 3, 1, 1)
        self.devD2Text = QLineEdit(self.gridLayoutWidget)
        self.devD2Text.setObjectName("devD2Text")
        self.devGridLayout.addWidget(self.devD2Text, 3, 1, 1, 1)
        self.devD3Text = QLineEdit(self.gridLayoutWidget)
        self.devD3Text.setObjectName("devD3Text")
        self.devGridLayout.addWidget(self.devD3Text, 3, 2, 1, 1)
        self.devD4Text = QLineEdit(self.gridLayoutWidget)
        self.devD4Text.setObjectName("devD4Text")
        self.devGridLayout.addWidget(self.devD4Text, 3, 3, 1, 1)
        self.windowGridLayout.addLayout(self.devGridLayout, 3, 2, 1, 1)
        self.sizeSubsCBox = QComboBox(self.gridLayoutWidget)
        self.sizeSubsCBox.setObjectName("sizeSubsCBox")
        self.windowGridLayout.addWidget(self.sizeSubsCBox, 2, 2, 1, 1)
        self.operatorText = QLineEdit(self.gridLayoutWidget)
        self.operatorText.setText("")
        self.operatorText.setObjectName("operatorText")
        self.windowGridLayout.addWidget(self.operatorText, 0, 2, 1, 1)
        self.sizeSubsLabel = QLabel(self.gridLayoutWidget)
        self.sizeSubsLabel.setObjectName("sizeSubsLabel")
        self.windowGridLayout.addWidget(self.sizeSubsLabel, 2, 0, 1, 1)
        self.operatorLabel = QLabel(self.gridLayoutWidget)
        self.operatorLabel.setObjectName("operatorLabel")
        self.windowGridLayout.addWidget(self.operatorLabel, 0, 0, 1, 1)
        self.holderTypeLabel = QLabel(self.gridLayoutWidget)
        self.holderTypeLabel.setObjectName("holderTypeLabel")
        self.windowGridLayout.addWidget(self.holderTypeLabel, 1, 0, 1, 1)
        self.holderTypeCBox = QComboBox(self.gridLayoutWidget)
        self.holderTypeCBox.setObjectName("holderTypeCBox")
        self.windowGridLayout.addWidget(self.holderTypeCBox, 1, 2, 1, 1)
        self.applyButton = QPushButton(self.centralwidget)
        self.applyButton.setGeometry(QRect(10, 560, 113, 32))
        self.applyButton.setObjectName("applyButton")
        self.buttonBox = QDialogButtonBox(self.centralwidget)
        self.buttonBox.setGeometry(QRect(590, 550, 164, 32))
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        MainWindow.setCentralWidget(self.centralwidget)
        #self.menubar = QMenuBar(MainWindow)
        #self.menubar.setGeometry(QtCore.QRect(0, 0, 789, 22))
        #self.menubar.setObjectName("menubar")
        #MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.devLabel.setText("Device labels")
        self.devA1Text.setText("A1")
        self.devB1Text.setText("B1")
        self.devC1Text.setText("C1")
        self.devD1Text.setText("D1")
        self.devA2Text.setText("A2")
        self.devA3Text.setText("A3")
        self.devA4Text.setText("A4")
        self.devB2Text.setText("B2")
        self.devB3Text.setText("B3")
        self.devB4Text.setText("B4")
        self.devC2Text.setText("C2")
        self.devC3Text.setText("C3")
        self.devC4Text.setText("C4")
        self.devD2Text.setText("D2")
        self.devD3Text.setText("D3")
        self.devD4Text.setText("D4")
        self.sizeSubsLabel.setText("Size of Substrate")
        self.operatorLabel.setText("Operator")
        self.holderTypeLabel.setText("Holder type")
        self.applyButton.setText("Apply")

        QMetaObject.connectSlotsByName(MainWindow)
