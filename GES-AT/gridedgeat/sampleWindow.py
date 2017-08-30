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

from . import logger

'''
   Sample Window
'''
class SampleWindow(QMainWindow):
    def __init__(self, parent=None):
        super(SampleWindow, self).__init__(parent)
        self.initUI(self)
    
    def initUI(self,MainWindow):
        self.setGeometry(10, 300, 440, 370)
        MainWindow.setWindowTitle("Devices configuration")
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
       
        self.sizeSubsCBox.addItem("1x1 in")
        self.sizeSubsCBox.setEnabled(False)
        self.holderTypeCBox.addItem(self.parent().config.numSubsHolderRow+"x"+self.parent().config.numSubsHolderRow)
        self.holderTypeCBox.setEnabled(False)
        
        self.commentsLabel = QLabel(self.centralwidget)
        self.commentsLabel.setObjectName("commentsLabel")
        self.commentsLabel.setGeometry(QRect(10, 150, 80, 20))
        #self.windowGridLayout.addWidget(self.commentsLabel, 3, 0, 1, 1)
        self.commentsText = QLineEdit(self.centralwidget)
        self.commentsText.setText("")
        self.commentsText.setGeometry(QRect(90, 150, 330, 20))
        self.commentsText.setObjectName("commentsText")
        #self.windowGridLayout.addWidget(self.commentsText, 3, 1, 1, 1)
       
        self.tableWidget = QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QRect(10, 190, 420, 145))
        self.tableWidget.setColumnCount(int(self.parent().config.numSubsHolderRow))
        self.tableWidget.setRowCount(int(self.parent().config.numSubsHolderCol))
        
        # This allows for background coloring of a cell
        for i in range(int(self.parent().config.numSubsHolderCol)):
            for j in range(int(self.parent().config.numSubsHolderRow)):
                self.tableWidget.setItem(i,j,QTableWidgetItem())
        #self.tableWidget.item(0, 0).setText("test-sample")

        self.tableWidget.itemDoubleClicked.connect(self.onCellClick)
        
        # This disable editing
        #self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # This enables editing by Double Click
        self.tableWidget.setEditTriggers(QAbstractItemView.SelectedClicked)

        self.loadButton = QPushButton(self.centralwidget)
        self.loadButton.setGeometry(QRect(310, 30, 100, 40))
        self.loadButton.setObjectName("loadButton")
        self.loadButton.clicked.connect(self.loadCsvDevices)
        self.saveButton = QPushButton(self.centralwidget)
        self.saveButton.setGeometry(QRect(310, 80, 100, 40))
        self.saveButton.setObjectName("saveButton")
        self.saveButton.clicked.connect(self.saveCsvDevices)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menuBar = QMenuBar(MainWindow)
        self.menuBar.setGeometry(QRect(0, 0, 774, 22))
        self.menuBar.setObjectName("menubar")
        
        self.loadMenu = QAction("&Load Devices", self)
        self.loadMenu.setShortcut("Ctrl+o")
        self.loadMenu.setStatusTip('Load device names and configuration from csv')
        self.loadMenu.triggered.connect(self.loadCsvDevices)
        fileMenu = self.menuBar.addMenu('&File')
        fileMenu.addAction(self.loadMenu)

        self.parent().viewWindowMenus(self.menuBar, self.parent())

        MainWindow.setMenuBar(self.menuBar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.sizeSubsLabel.setText("Size of Substrate ")
        self.operatorLabel.setText("Operator")
        self.holderTypeLabel.setText("Holder type")
        self.commentsLabel.setText("Comments")
        self.loadButton.setText("Load")
        self.saveButton.setText("Save")

    @pyqtSlot()
    def onCellClick(self):
        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            print(" Selected cell: (",self.tableWidget.row(currentQTableWidgetItem),
                ", ",self.tableWidget.column(currentQTableWidgetItem),")")

    # Enable and disable fields (flag is either True or False) during acquisition.
    def enableSamplePanel(self, flag):
        self.holderTypeCBox.setEnabled(flag)
        self.operatorText.setEnabled(flag)
        self.sizeSubsCBox.setEnabled(flag)
        self.loadButton.setEnabled(flag)
        self.tableWidget.setEnabled(flag)

    # Change color in sample cells depending on the acqusition status
    def colorCellAcq(self,row,column,color):
        if color is "red":
            self.tableWidget.item(row, column).setBackground(QColor(255,0,0))
        if color is "white":
            self.tableWidget.item(row, column).setBackground(QColor(255,255,255))
        if color is "green":
            self.tableWidget.item(row, column).setBackground(QColor(0,255,0))

    # Reset color in sample cells to white
    def resetCellAcq(self):
        for i in range(int(self.parent().config.numSubsHolderCol)):
            for j in range(int(self.parent().config.numSubsHolderRow)):
                self.tableWidget.item(i, j).setBackground(QColor(255,255,255))

    # Load device names and configuration
    def loadCsvDevices(self):
        import csv
        try:
            filename = QFileDialog.getOpenFileName(self,
                        "Open CSV device file", "","*.csv")
            with open(filename[0], 'rU') as inputFile:
                input = csv.reader(inputFile)
                devConf=[]
                for row in input:
                    devConf.append(row)
            for i in range(int(self.parent().config.numSubsHolderRow)):
                for j in range(int(self.parent().config.numSubsHolderCol)):
                    try:
                        self.tableWidget.item(i,j).setText(devConf[i][j])
                    except:
                        pass
            print("Device configuration loaded from:",filename[0])
            logger.info("Device configuration loaded from:"+filename[0])
        except:
            print("Error in loading device configuration")
            logger.info("Error in loading device configuration")

    # Save device names and configuration
    def saveCsvDevices(self):
        import csv
        devConf=[['']*4 for i in range(4)]
        for i in range(int(self.parent().config.numSubsHolderRow)):
            for j in range(int(self.parent().config.numSubsHolderCol)):
                devConf[i][j] = self.tableWidget.item(i,j).text()
        try:
            filename = QFileDialog.getSaveFileName(self,
                    "Save CSV device file", "","*.csv")
            with open(filename[0], 'w') as inputFile:
                csvwrite = csv.writer(inputFile)
                for i in range(int(self.parent().config.numSubsHolderRow)):
                    csvwrite.writerow(devConf[i])
            print("Device configuration saved to:",filename[0])
            logger.info("Device configuration saved to:"+filename[0])
        except:
            print("Error in saving device configuration")
            logger.info("Error in saving device configuration")


