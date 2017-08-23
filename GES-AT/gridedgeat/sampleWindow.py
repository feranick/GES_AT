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
    QVBoxLayout,QGridLayout,QLabel,QGraphicsView,QFileDialog,QStatusBar,QTableWidget,
    QGraphicsScene,QLineEdit,QMessageBox,QDialog,QComboBox,QMenuBar,QDialogButtonBox,
    QAbstractItemView,QTableWidgetItem,)
from PyQt5.QtGui import (QIcon,QImage,QKeySequence,QPixmap,QPainter,QColor)
from PyQt5.QtCore import (pyqtSlot,QRectF,QRect,QCoreApplication,QSize)

from . import config

'''
   Sample Window
'''
class SampleWindow(QMainWindow):
    def __init__(self):
        super(SampleWindow, self).__init__()
        self.initUI(self)
    
    def initUI(self,MainWindow):
        MainWindow.resize(440, 330)
        MainWindow.setWindowTitle("Sample configuration")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayoutWidget = QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QRect(10, 0, 275, 150))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.windowGridLayout = QGridLayout(self.gridLayoutWidget)
        self.windowGridLayout.setContentsMargins(0, 0, 0, 0)
        self.windowGridLayout.setSpacing(1)
        self.windowGridLayout.setObjectName("windowGridLayout")
        self.holderTypeCBox = QComboBox(self.gridLayoutWidget)
        self.holderTypeCBox.setObjectName("holderTypeCBox")
        self.windowGridLayout.addWidget(self.holderTypeCBox, 1, 1, 1, 1)
        self.sizeSubsLabel = QLabel(self.gridLayoutWidget)
        self.sizeSubsLabel.setObjectName("sizeSubsLabel")
        self.windowGridLayout.addWidget(self.sizeSubsLabel, 2, 0, 1, 1)
        self.holderTypeLabel = QLabel(self.gridLayoutWidget)
        self.holderTypeLabel.setObjectName("holderTypeLabel")
        self.windowGridLayout.addWidget(self.holderTypeLabel, 1, 0, 1, 1)
        self.operatorLabel = QLabel(self.gridLayoutWidget)
        self.operatorLabel.setObjectName("operatorLabel")
        self.windowGridLayout.addWidget(self.operatorLabel, 0, 0, 1, 1)
        self.operatorText = QLineEdit(self.gridLayoutWidget)
        self.operatorText.setText("")
        self.operatorText.setObjectName("operatorText")
        self.windowGridLayout.addWidget(self.operatorText, 0, 1, 1, 1)
        self.sizeSubsCBox = QComboBox(self.gridLayoutWidget)
        self.sizeSubsCBox.setObjectName("sizeSubsCBox")
        self.windowGridLayout.addWidget(self.sizeSubsCBox, 2, 1, 1, 1)
       
        self.tableWidget = QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QRect(10, 150, 420, 145))
        self.tableWidget.setColumnCount(config.numSubsHolderRow)
        self.tableWidget.setRowCount(config.numSubsHolderCol)
        #self.tableWidget.setItem(0,0, QTableWidgetItem(""))
        
        # This allows for background coloring of a cell
        self.tableWidget.setItem(0,0,QTableWidgetItem())
        self.tableWidget.item(0, 0).setBackground(QColor(255,0,0))
        self.tableWidget.item(0, 0).setText("test-sample")

        self.tableWidget.itemClicked.connect(self.onCellClick)
        
        # This disable editing
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # This enables editing by Double Click
        self.tableWidget.setEditTriggers(QAbstractItemView.DoubleClicked)

        self.applyButton = QPushButton(self.centralwidget)
        self.applyButton.setGeometry(QRect(310, 30, 100, 100))
        self.applyButton.setObjectName("applyButton")

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setGeometry(QRect(0, 0, 774, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.sizeSubsLabel.setText("Size of Substrate ")
        self.operatorLabel.setText("Operator")
        self.holderTypeLabel.setText("Holder type")
        self.applyButton.setText("Apply")

    @pyqtSlot()
    def onCellClick(self):
        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            print("Selected cell: ",currentQTableWidgetItem.text())

    # Enable and disable fields (flag is either True or False) during acquisition.
    def enableSamplePanel(self, flag):
        self.holderTypeCBox.setEnabled(flag)
        self.operatorText.setEnabled(flag)
        self.sizeSubsCBox.setEnabled(flag)
        self.applyButton.setEnabled(flag)
        self.tableWidget.setEnabled(flag)

    def colorCellAcq(self,row,column,color):
        if color is "red":
            self.tableWidget.item(row, col).setBackground(QColor(255,0,0))
        if color is "white":
            self.tableWidget.item(row, col).setBackground(QColor(255,255,255))
        if color is "green":
            self.tableWidget.item(row, col).setBackground(QColor(0,255,0))


