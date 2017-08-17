'''
mainWindow
-------------
Various classes for providing a graphical user interface

Copyright (C) 2017 Nicola Ferralis <ferralis@mit.edu>
Copyright (C) 2017 Auto-testing team - MIT GridEdge Solar

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

'''

import sys, webbrowser, random, time
from datetime import datetime
from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton, QWidget, QAction,
    QVBoxLayout,QGridLayout,QLabel,QGraphicsView,QFileDialog,QStatusBar,
    QGraphicsScene,QLineEdit,QMessageBox,QDialog)
from PyQt5.QtGui import (QIcon,QImage,QKeySequence,QPixmap,QPainter)
from PyQt5.QtCore import (pyqtSlot,QRectF)

from . import config
from . import __version__
from . import __author__
from .cameraWindow import *
from .resultsWindow import *
from .sampleWindow import *
from .acquisition import *
from .acquisitionWindow import *
from .dataManagement import *

'''
   Main Window
   Definition of Main Panel
'''
class MainWindow(QMainWindow):
 
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("GridEdge AutoTesting %s" % __version__)
        self.setGeometry(10,30,350,175)
        self.aboutwid = AboutWidget()
        self.samplewind = SampleWindow()
        self.acquisitionwind = AcquisitionWindow()
        self.resultswind = ResultsWindow()
        self.camerawind = CameraWindow()
        self.weblinks = WebLinksWidget()
        self.acquisition = Acquisition()
        self.dbconnectionwid = DBConnection()
     
        #### define actions ####
        # actions for "File" menu
        #self.fileOpenAction = self.createAction("&Open...", self.camerawind.fileOpen,
        #        QKeySequence.Open, None,
        #        "Open a directory containing the image files.")
        self.fileQuitAction = self.createAction("&Quit", self.fileQuit,
                QKeySequence("Ctrl+q"), None,
                "Close the application")
                
        self.fileActions = [None, self.fileQuitAction]
        
        # actions for "Instruments" menu
        self.stageAction = self.createAction("&Stage", self.aboutwid.show,
                QKeySequence("Ctrl+s"), None,
                "Stage")
        
        self.powermeterAction = self.createAction("&Powermeter", self.aboutwid.show,
                QKeySequence("Ctrl+p"), None,
                "Powermeter")
        self.cameraAction = self.createAction("&Camera", self.camerawind.show,
                QKeySequence("Ctrl+c"), None,
                "Camera panel")

        self.instrumentsActions = [None, self.powermeterAction, None,
                        self.cameraAction, None, self.stageAction]

        # actions for "Tools" menu
        self.dbConnectionAction = self.createAction("&TestDBConnection", self.dbconnectionwid.show,
                QKeySequence("Ctrl+T"), None,
                "Test connectivity to data-management")
        
        self.toolsActions = [None, self.dbConnectionAction]
                
        # actions for "Help" menu
        self.helpAction = self.createAction("&Help", self.weblinks.help,
                None, None,
                "Show help")
        self.devAction = self.createAction("&Development and Bugs", self.weblinks.dev,
                None, None,
                "Development and Bugs")
        self.aboutAction = self.createAction("&About", self.aboutwid.show,
                None, None,
                "About GridEdge AutoTesting")
        self.helpActions = [None, self.helpAction, None, self.devAction,
                None, self.aboutAction]
                
        #### Create menu bar ####
        fileMenu = self.menuBar().addMenu("&File")
        self.addActions(fileMenu, self.fileActions)

        instrumentsMenu = self.menuBar().addMenu("&Instruments")
        self.addActions(instrumentsMenu, self.instrumentsActions)

        toolsMenu = self.menuBar().addMenu("&Tools")
        self.addActions(toolsMenu, self.toolsActions)

        helpMenu = self.menuBar().addMenu("&Help")
        self.addActions(helpMenu, self.helpActions)
                
        #### define actions ####
        # actions for "Buttons" menu
        self.sampleAction = self.createAction("&Sample", self.samplewind.show,
                QKeySequence("Ctrl+s"), None,
                "Sample panel")
        self.acquisitionAction = self.createAction("&Acquisition", self.acquisitionwind.show,
                QKeySequence("Ctrl+r"), None,
                "Acquisition Setup panel")
        self.resultsAction = self.createAction("&Results", self.resultswind.show,
                QKeySequence("Ctrl+p"), None,
                "Results panel")
    
        #### Create tool bar ####
        toolBar = self.addToolBar("&Toolbar")
        # adding actions to the toolbar, addActions-function creates a separator with "None"
        self.toolBarActions = [self.sampleAction, None, self.acquisitionAction, None, self.resultsAction, None,
                               self.cameraAction, None]
        self.addActions(toolBar, self.toolBarActions)
        
        #### Create status bar ####
        self.statusBar().showMessage("Ready", 5000)
    
        #### Create basic push buttons to run acquisition ####
        self.startAcqButton = QPushButton(self)
        self.startAcqButton.setGeometry(QRect(20, 90, 150, 50))
        self.startAcqButton.setObjectName("Start Acquisition")
        self.startAcqButton.setText("Start Acquisition")
        self.startAcqButton.clicked.connect(self.acquisition.start)
        self.stopAcqButton = QPushButton(self)
        self.stopAcqButton.setGeometry(QRect(190, 90, 150, 50))
        self.stopAcqButton.setObjectName("Stop Acquisition")
        self.stopAcqButton.setText("Stop Acquisition")
        self.stopAcqButton.clicked.connect(self.acquisition.stop)
        self.logo = QLabel(self)
        self.logo.setGeometry(QRect(30, 30, 311, 61))
        self.logo.setText("")
        self.logo.setPixmap(QPixmap("gridedgeat/rsrc/logo.png"))
        self.logo.setObjectName("logo")

    def createAction(self, text, slot=None, shortcut=None, icon=None,
                     tip=None, checkable=False, signal="triggered()"):
        """ Convenience function that creates an action with the specified attributes. """
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/{0}.png".format(icon)))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            action.triggered.connect(slot)
        if checkable:
            action.setCheckable(True)
        return action
            
    def addActions(self, target, actions):
        """
        Convenience function that adds the actions to the target.
        If an action is None a separator will be added.
        
        """
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def fileQuit(self):
        """Special quit-function as the normal window closing might leave something on the background """
        QApplication.closeAllWindows()

'''
   WebLinks Widget
   Definition of Web links
'''
class WebLinksWidget():
    def __init__(self):
        super(WebLinksWidget, self).__init__()

    def help(self):
        webbrowser.open("https://sites.google.com/site/gridedgesolar/")
    def dev(self):
        webbrowser.open("https://github.mit.edu/GridEdgeSolar/Autotesting")

'''
   About Widget
   Definition of About Panel
'''
class AboutWidget(QWidget):
    """ PyQt widget for About Box Panel """
    
    def __init__(self):
        super(AboutWidget, self).__init__()
        self.initUI()
    
    def initUI(self):
        self.setGeometry(100, 200, 400, 300)
        self.setWindowTitle('About GridEdge AutoTesting')
    
        self.gridLayout = QGridLayout()
        self.setLayout(self.gridLayout)
        self.verticalLayout = QVBoxLayout()
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)
        
        self.logo = QLabel(self)
        self.logo.setGeometry(QRect(30, 30, 311, 61))
        self.logo.setText("GridEdge Solar @ MIT")
        self.logo.setPixmap(QPixmap("gridedgeat/rsrc/logo.png"))
        self.logo.setObjectName("logo")

        self.labelTitle = QLabel("<qt><b><big><a href = http://gridedgesolar.com>Autotesting %s</a></b></big></qt>" % __version__, self)
        self.labelBy = QLabel("by: %s" % __author__, self)
        self.labelContact = QLabel("<qt>Contact: <a href = mailto:mitgridedge@gmail.com> mitgridedge@gmail.com</a></qt>", self)
        self.labelDetails = QLabel("GridEdgeSolar is a Solar PV project at MIT", self)
        self.labelLicense = QLabel("This software is licensed under the GNU GPL v.2.0 or later", self)
        
        for label in [self.logo, self.labelTitle, self.labelBy,
                self.labelContact, self.labelDetails, self.labelLicense]:
            label.setWordWrap(True)
            label.setOpenExternalLinks(True);
            self.verticalLayout.addWidget(label)

'''
   DBConnection Widget
   Definition of Database connection Widget
'''
class DBConnection(QWidget):
    """ PyQt widget for About Box Panel """
    
    def __init__(self):
        super(DBConnection, self).__init__()
        self.initUI(self)
    
    def initUI(self,Panel):
        self.setGeometry(100, 200, 400, 330)
        self.setWindowTitle('Testing connectivity to Data-management')
        self.gridLayoutWidget = QWidget(Panel)
        self.gridLayoutWidget.setGeometry(QRect(19, 9, 361, 221))
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
        self.dbTestConnectButton.setGeometry(QRect(20, 280, 361, 32))
        self.dbTestConnectButton.setObjectName("dbTestConnectButton")
        self.dbConnectResultLabel = QLabel(Panel)
        self.dbConnectResultLabel.setGeometry(QRect(30, 250, 321, 20))
        self.dbConnectResultLabel.setObjectName("dbConnectResultLabel")

        self.dbHostnameLabel.setText("DB hostname IP")
        self.dbPortNumLabel.setText("DB port number")
        self.dbNameLabel.setText("DB name")
        self.dbUsernameLabel.setText("DB Username")
        self.dbPasswordLabel.setText("DB Password")
        self.dbTestConnectButton.setText("Test Connectivity")
        self.dbConnectResultLabel.setText("")

        self.dbHostnameText.setText(config.DbHostname)
        self.dbPortNumText.setText(str(config.DbPortNumber))
        self.dbNameText.setText(config.DbName)
        self.dbUsernameText.setText(config.DbUsername)
        self.dbPasswordText.setText(config.DbPassword)
        
        self.dbConnectInfo = [config.DbHostname,config.DbPortNumber,
                config.DbName,config.DbUsername,config.DbPassword]
        
        self.dbTestConnectButton.clicked.connect(self.dbCheckConnect)

    def dbCheckConnect(self):
        self.dbConnect = DataManagementDB(self.dbConnectInfo)
        try:
            self.dbConnect.connectDB()
            self.dbConnectResultLabel.setText("Connection successful")
        except:
            self.dbConnectResultLabel.setText("Connection failed")

