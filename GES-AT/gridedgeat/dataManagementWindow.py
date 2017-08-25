'''
Data Management Window
------------------
Class for providing a graphical user interface for 
Data Management Window

Copyright (C) 2017 Nicola Ferralis <ferralis@mit.edu>
Copyright (C) 2017 Auto-testing team - MIT GridEdge Solar

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

'''

import sys
from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton, QWidget, QAction,
    QVBoxLayout,QGridLayout,QLabel,QGraphicsView,QFileDialog,QStatusBar,QTableWidget,
    QGraphicsScene,QLineEdit,QMessageBox,QDialog,QComboBox,QMenuBar,QDialogButtonBox,
    QAbstractItemView,QTableWidgetItem,)
from PyQt5.QtGui import (QIcon,QImage,QKeySequence,QPixmap,QPainter,QColor)
from PyQt5.QtCore import (pyqtSlot,QRectF,QRect,QCoreApplication,QSize)

from . import config
from .dataManagement import *

'''
   DBConnection Widget
   Definition of Database connection Widget
'''
class DBConnection(QWidget):    
    def __init__(self):
        super(DBConnection, self).__init__()
        self.initUI(self)
    
    def initUI(self,Panel):
        self.setGeometry(10, 200, 250, 300)
        self.setWindowTitle('Data-management Settings')
        self.gridLayoutWidget = QWidget(Panel)
        self.gridLayoutWidget.setGeometry(QRect(10, 9, 230, 221))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(10, 0, 10, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.dbHostnameLabel = QLabel(self.gridLayoutWidget)
        self.dbHostnameLabel.setObjectName("dbHostnameLabel")
        self.gridLayout.addWidget(self.dbHostnameLabel, 0, 0, 1, 1)
        self.dbHostnameText = QLineEdit(self.gridLayoutWidget)
        self.dbHostnameText.setObjectName("dbHostnameText")
        self.gridLayout.addWidget(self.dbHostnameText, 0, 1, 1, 1)
        self.dbUsernameText = QLineEdit(self.gridLayoutWidget)
        self.dbUsernameText.setObjectName("dbUsernameText")
        self.gridLayout.addWidget(self.dbUsernameText, 3, 1, 1, 1)
        self.dbNameText = QLineEdit(self.gridLayoutWidget)
        self.dbNameText.setObjectName("dbNameText")
        self.gridLayout.addWidget(self.dbNameText, 2, 1, 1, 1)
        self.dbPortNumText = QLineEdit(self.gridLayoutWidget)
        self.dbPortNumText.setObjectName("dbPortNumText")
        self.gridLayout.addWidget(self.dbPortNumText, 1, 1, 1, 1)
        self.dbPasswordText = QLineEdit(self.gridLayoutWidget)
        self.dbPasswordText.setObjectName("dbPasswordText")
        self.gridLayout.addWidget(self.dbPasswordText, 4, 1, 1, 1)
        self.dbPortNumLabel = QLabel(self.gridLayoutWidget)
        self.dbPortNumLabel.setObjectName("dbPortNumLabel")
        self.gridLayout.addWidget(self.dbPortNumLabel, 1, 0, 1, 1)
        self.dbNameLabel = QLabel(self.gridLayoutWidget)
        self.dbNameLabel.setObjectName("dbNameLabel")
        self.gridLayout.addWidget(self.dbNameLabel, 2, 0, 1, 1)
        self.dbUsernameLabel = QLabel(self.gridLayoutWidget)
        self.dbUsernameLabel.setObjectName("dbUsernameLabel")
        self.gridLayout.addWidget(self.dbUsernameLabel, 3, 0, 1, 1)
        self.dbPasswordLabel = QLabel(self.gridLayoutWidget)
        self.dbPasswordLabel.setObjectName("dbPasswordLabel")
        self.gridLayout.addWidget(self.dbPasswordLabel, 4, 0, 1, 1)
        self.dbTestConnectButton = QPushButton(Panel)
        self.dbTestConnectButton.setGeometry(QRect(10, 260, 230, 30))
        self.dbTestConnectButton.setObjectName("dbTestConnectButton")
        self.dbConnectResultLabel = QLabel(Panel)
        self.dbConnectResultLabel.setGeometry(QRect(20, 230, 321, 20))
        self.dbConnectResultLabel.setObjectName("dbConnectResultLabel")

        self.dbHostnameLabel.setText("DB hostname IP")
        self.dbPortNumLabel.setText("DB port number")
        self.dbNameLabel.setText("DB name")
        self.dbUsernameLabel.setText("DB Username")
        self.dbPasswordLabel.setText("DB Password")
        self.dbTestConnectButton.setText("Test Connectivity")
        self.dbConnectResultLabel.setText("Idle")

        self.dbHostnameText.setText(config.DbHostname)
        self.dbPortNumText.setText(str(config.DbPortNumber))
        self.dbNameText.setText(config.DbName)
        self.dbUsernameText.setText(config.DbUsername)
        self.dbPasswordText.setText(config.DbPassword)
        
        self.dbTestConnectButton.clicked.connect(self.dbCheckConnect)
    
    def getDbConnectionInfo(self):
        self.dbConnectInfo = [self.dbHostnameText.text(),
                    self.dbPortNumText.text(),
                    self.dbNameText.text(),
                    self.dbUsernameText.text(),
                    self.dbPasswordText.text()]

    def dbCheckConnect(self):
        self.getDbConnectionInfo()
        self.dbConnect = DataManagementDB(self.dbConnectInfo)
        try:
            if self.dbConnect.connectDB()[1] is True:
                self.dbConnectResultLabel.setText("Connection successful")
        except:
            self.dbConnectResultLabel.setText("Connection failed")