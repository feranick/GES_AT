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
from .powermeterWindow import *
from .stageWindow import *
from .dataManagement import *
from .dataManagementWindow import *

'''
   Main Window
   Definition of Main Panel
'''
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__(None)
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("GridEdge AutoTesting %s" % __version__)
        self.setGeometry(10,30,350,200)
        self.aboutwid = AboutWidget()
        self.samplewind = SampleWindow(parent=self)
        self.resultswind = ResultsWindow(parent=self)
        self.camerawind = CameraWindow(parent=self)
        self.weblinks = WebLinksWidget()
        self.acquisition = Acquisition()
        self.acquisitionwind = AcquisitionWindow(parent=self)
        self.powermeterwind = PowermeterWindow(parent=self)
        self.stagewind = StageWindow(parent=self)
        self.dbconnectionwind = DataManagementWindow(parent=self)
        
        # Create menu
        self.menuBar = QMenuBar(self)
        self.quitMenu = QAction("&Quit", self)
        self.quitMenu.setShortcut("Ctrl+q")
        self.quitMenu.setStatusTip('Quit')
        self.quitMenu.triggered.connect(self.fileQuit)
        
        fileMenu = self.menuBar.addMenu('&File')
        fileMenu.addAction(self.quitMenu)
        
        self.powermeterMenu = QAction("&Powermeter", self)
        self.powermeterMenu.setShortcut("Ctrl+p")
        self.powermeterMenu.setStatusTip('Powermeter controls')
        self.powermeterMenu.triggered.connect(self.powermeterwind.show)
        self.stageMenu = QAction("&Stage", self)
        self.stageMenu.setShortcut("Ctrl+x")
        self.stageMenu.setStatusTip('Stage controls')
        self.stageMenu.triggered.connect(self.stagewind.show)
        self.cameraMenu = QAction("&Camera", self)
        self.cameraMenu.setShortcut("Ctrl+c")
        self.cameraMenu.setStatusTip('Camera controls')
        self.cameraMenu.triggered.connect(self.camerawind.show)

        instrumentsMenu = self.menuBar.addMenu('&Instruments')
        instrumentsMenu.addAction(self.powermeterMenu)
        instrumentsMenu.addAction(self.stageMenu)
        instrumentsMenu.addAction(self.cameraMenu)
        
        self.dataManagementMenu = QAction("&Data Management", self)
        self.dataManagementMenu.setShortcut("Ctrl+d")
        self.dataManagementMenu.setStatusTip('Data Management Settings')
        self.dataManagementMenu.triggered.connect(self.dbconnectionwind.show)
        
        toolsMenu = self.menuBar.addMenu('&Tools')
        toolsMenu.addAction(self.dataManagementMenu)
        
        self.viewWindowMenus(self.menuBar, self)

        self.helpMenu = QAction("&Help", self)
        self.helpMenu.setShortcut("Ctrl+h")
        self.helpMenu.setStatusTip('Help')
        self.helpMenu.triggered.connect(self.weblinks.help)
        self.devBugsMenu = QAction("&Development and Bugs", self)
        self.devBugsMenu.setShortcut("Ctrl+b")
        self.devBugsMenu.setStatusTip('Development and bugs')
        self.devBugsMenu.triggered.connect(self.weblinks.help)
        self.aboutMenu = QAction("&About", self)
        self.aboutMenu.setShortcut("Ctrl+a")
        self.aboutMenu.setStatusTip('About')
        self.aboutMenu.triggered.connect(self.aboutwid.show)
        
        aboutMenu = self.menuBar.addMenu('&Help')
        aboutMenu.addAction(self.helpMenu)
        aboutMenu.addAction(self.devBugsMenu)
        aboutMenu.addSeparator()
        aboutMenu.addAction(self.aboutMenu)
        
        #### Create tool bar ####
        self.sampleToolbar = QAction("&Sample", self)
        self.sampleToolbar.setShortcut("Ctrl+s")
        self.sampleToolbar.setStatusTip('Sample Configuration')
        self.sampleToolbar.triggered.connect(self.samplewind.show)
        
        self.acquisitionToolbar = QAction("&Acquisition", self)
        self.acquisitionToolbar.setShortcut("Ctrl+a")
        self.acquisitionToolbar.setStatusTip('Acquisition paramenters')
        self.acquisitionToolbar.triggered.connect(self.acquisitionwind.show)
        
        self.resultsToolbar = QAction("&Results", self)
        self.resultsToolbar.setShortcut("Ctrl+p")
        self.resultsToolbar.setStatusTip('Results Panel')
        self.resultsToolbar.triggered.connect(self.resultswind.show)
        
        toolBar = self.addToolBar("&Toolbar")
        toolBar.addAction(self.sampleToolbar)
        toolBar.addSeparator()
        toolBar.addAction(self.acquisitionToolbar)
        toolBar.addSeparator()
        toolBar.addAction(self.resultsToolbar)
        toolBar.addSeparator()
       
        #### Create status bar ####
        self.statusBar().showMessage("Ready", 5000)
    
        #### Create basic push buttons to run acquisition ####
        self.startAcqButton = QPushButton(self)
        self.startAcqButton.setGeometry(QRect(10, 120, 160, 50))
        self.startAcqButton.setObjectName("Start Acquisition")
        self.startAcqButton.setText("Start Acquisition")
        self.startAcqButton.clicked.connect(lambda: self.acquisition.start(self))
        self.stopAcqButton = QPushButton(self)
        self.stopAcqButton.setGeometry(QRect(170, 120, 160, 50))
        self.stopAcqButton.setObjectName("Stop Acquisition")
        self.stopAcqButton.setText("Stop Acquisition")
        self.stopAcqButton.clicked.connect(lambda: self.acquisition.stop(self))
        self.logo = QLabel(self)
        self.logo.setGeometry(QRect(20, 55, 311, 61))
        self.logo.setText("")
        self.logo.setPixmap(QPixmap("gridedgeat/rsrc/logo.png"))
        self.logo.setObjectName("logo")
    
    def fileQuit(self):
        """Special quit-function as the normal window closing might leave something on the background """
        QApplication.closeAllWindows()
    
    def enableButtonsAcq(self,flag):
        if flag is False:
            self.startAcqButton.setText("Acquisition Running...")
        else:
            self.startAcqButton.setText("Start Acquisition")
        self.startAcqButton.setEnabled(flag)

    # Adds Menus to expose other Windows.
    def viewWindowMenus(self, menuObj, obj):
        viewMainWindowMenu = QAction("&Main Window", self)
        viewMainWindowMenu.setShortcut("Ctrl+m")
        viewMainWindowMenu.setStatusTip('Display Main Window')
        viewMainWindowMenu.triggered.connect(lambda: self.displayMainWindow(obj))
        viewSampleMenu = QAction("&Device Window", self)
        viewSampleMenu.setShortcut("Ctrl+d")
        viewSampleMenu.setStatusTip('Display Device Window')
        viewSampleMenu.triggered.connect(lambda: self.displayMainWindow(obj.samplewind))
        viewAcquisitionMenu = QAction("&Acquisition Window", self)
        viewAcquisitionMenu.setShortcut("Ctrl+a")
        viewAcquisitionMenu.setStatusTip('Display Acquisition Window')
        viewAcquisitionMenu.triggered.connect(lambda: self.displayMainWindow(obj.acquisitionwind))
        viewResultsMenu = QAction("&Results Window", self)
        viewResultsMenu.setShortcut("Ctrl+r")
        viewResultsMenu.setStatusTip('Display Results Window')
        viewResultsMenu.triggered.connect(lambda: self.displayMainWindow(obj.resultswind))

        windowMenu = menuObj.addMenu('&Window')
        windowMenu.addAction(viewMainWindowMenu)
        windowMenu.addAction(viewSampleMenu)
        windowMenu.addAction(viewAcquisitionMenu)
        windowMenu.addAction(viewResultsMenu)

    def displayMainWindow(self, obj):
        obj.show()
        obj.setWindowState(obj.windowState() & Qt.WindowMinimized | Qt.WindowActive)
        obj.raise_()
        obj.activateWindow()

    def closeEvent(self, event):
        quit_msg = "Are you sure you want to exit the program?"
        reply = QMessageBox.question(self, 'Message',
                     quit_msg, QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.close()
        else:
            event.ignore()

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
        self.logo.setPixmap(QPixmap("gridedgeat/rsrc/logo_about.png"))
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


