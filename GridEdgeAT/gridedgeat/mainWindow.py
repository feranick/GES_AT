'''
mainWindow
-------------
Various classes for providing a graphical user interface

Copyright (C) 2017 Nicola Ferralis <ferralis@mit.edu>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

'''

import sys, webbrowser, random, time
import configparser
from datetime import datetime

from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton,
    QWidget, QAction,QVBoxLayout,QGridLayout,QLabel,QGraphicsView,
    QFileDialog,QStatusBar,QGraphicsScene,QLineEdit,QMessageBox,
    QDialog,QToolBar,QMenuBar)
from PyQt5.QtGui import (QIcon,QImage,QKeySequence,QPixmap,QPainter)
from PyQt5.QtCore import (pyqtSlot,QRectF)

from . import __version__
from . import __author__
from . import logger
from .configuration import *
from .cameraWindow import *
from .resultsWindow import *
from .sampleWindow import *
from .acquisition import *
from .acquisitionWindow import *
from .powermeterWindow import *
from .stageWindow import *
from .sourcemeterWindow import *
from .switchboxWindow import *
from .shutterWindow import *
from .dataManagement import *
from .dataManagementWindow import *

'''
   Main Window
   Definition of Main Panel
'''
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__(None)
        self.config = Configuration()
        self.config.readConfig(self.config.configFile)
        self.initUI()
    
    # Define UI elements
    def initUI(self):
        logger.info("Gridedge Auto-testing v."+__version__)
        self.setWindowTitle("GridEdge AutoTesting %s" % __version__)
        self.setGeometry(10,30,340,220)
        self.setFixedSize(self.size())
        self.aboutwid = AboutWidget()
        self.samplewind = SampleWindow(parent=self)
        self.resultswind = ResultsWindow(parent=self)
        self.camerawind = CameraWindow(parent=self)
        self.weblinks = WebLinksWidget()
        self.acquisition = Acquisition(parent=self)
        self.acquisitionwind = AcquisitionWindow(parent=self)
        self.powermeterwind = PowermeterWindow(parent=self)
        self.stagewind = StageWindow(parent=self)
        self.sourcemeterwind = SourcemeterWindow(parent=self)
        self.switchboxwind = SwitchboxWindow(parent=self)
        self.shutterwind = ShutterWindow(parent=self)
        self.dbconnectionwind = DataManagementWindow(parent=self)
        
        # Create menu and toolbar
        self.menuBar = QMenuBar(self)
        self.menuBar.setGeometry(0,0,340,25)
        self.toolBar = QToolBar(self)
        self.toolBar.setGeometry(0,170,340,25)

        # Menu entries
        self.loadConfigMenu = QAction("&Load Configuration", self)
        self.loadConfigMenu.setShortcut("Ctrl+Shift+l")
        self.loadConfigMenu.setStatusTip('Quit')
        self.loadConfigMenu.triggered.connect(self.loadConfig)
        
        self.saveConfigMenu = QAction("&Save Configuration", self)
        self.saveConfigMenu.setShortcut("Ctrl+Shift+s")
        self.saveConfigMenu.setStatusTip('Quit')
        self.saveConfigMenu.triggered.connect(self.saveConfig)
        
        self.loadMenu = QAction("&Load Data", self)
        self.loadMenu.setShortcut("Ctrl+o")
        self.loadMenu.setStatusTip('Load csv data from saved file')
        self.loadMenu.triggered.connect(self.resultswind.read_csv)
        
        self.directoryMenu = QAction("&Set directory for saved files", self)
        self.directoryMenu.setShortcut("Ctrl+d")
        self.directoryMenu.setStatusTip('Set directory for saved files')
        self.directoryMenu.triggered.connect(self.resultswind.set_dir_saved)
        
        self.quitMenu = QAction("&Quit", self)
        self.quitMenu.setShortcut("Ctrl+q")
        self.quitMenu.setStatusTip('Quit')
        self.quitMenu.triggered.connect(self.fileQuit)
        
        fileMenu = self.menuBar.addMenu('&File')
        fileMenu.addAction(self.quitMenu)
        fileMenu.addSeparator()
        fileMenu.addAction(self.loadMenu)
        fileMenu.addAction(self.directoryMenu)
        fileMenu.addSeparator()
        fileMenu.addAction(self.loadConfigMenu)
        fileMenu.addAction(self.saveConfigMenu)
        
        self.stageMenu = QAction("&Stage", self)
        self.stageMenu.setShortcut("Ctrl+x")
        self.stageMenu.setStatusTip('Stage controls')
        self.stageMenu.triggered.connect(self.stagewind.show)
        self.powermeterMenu = QAction("&Powermeter", self)
        self.powermeterMenu.setShortcut("Ctrl+p")
        self.powermeterMenu.setStatusTip('Powermeter controls')
        self.powermeterMenu.triggered.connect(self.showPowermeterShutter)
        self.shutterMenu = QAction("&Shutter", self)
        self.shutterMenu.setShortcut("Ctrl+e")
        self.shutterMenu.setStatusTip('Shutter controls')
        self.shutterMenu.triggered.connect(self.shutterwind.show)
        self.sourcemeterMenu = QAction("&Sourcemeter", self)
        self.sourcemeterMenu.setShortcut("Ctrl+k")
        self.sourcemeterMenu.setStatusTip('Sourcemeter controls')
        self.sourcemeterMenu.triggered.connect(self.sourcemeterwind.show)
        self.switchboxMenu = QAction("&Switchbox", self)
        self.switchboxMenu.setShortcut("Ctrl+b")
        self.switchboxMenu.setStatusTip('Switchbox controls')
        self.switchboxMenu.triggered.connect(self.switchboxwind.show)
        self.cameraMenu = QAction("&Camera Alignment", self)
        self.cameraMenu.setShortcut("Ctrl+c")
        self.cameraMenu.setStatusTip('Camera controls')
        self.cameraMenu.triggered.connect(self.showCameraSample)

        instrumentsMenu = self.menuBar.addMenu('&Instruments')
        instrumentsMenu.addAction(self.cameraMenu)
        instrumentsMenu.addAction(self.powermeterMenu)
        instrumentsMenu.addSeparator()
        instrumentsMenu.addAction(self.stageMenu)
        instrumentsMenu.addAction(self.shutterMenu)
        instrumentsMenu.addSeparator()
        instrumentsMenu.addAction(self.sourcemeterMenu)
        instrumentsMenu.addAction(self.switchboxMenu)
        
        self.dataManagementMenu = QAction("&Data Management", self)
        self.dataManagementMenu.setShortcut("Ctrl+m")
        self.dataManagementMenu.setStatusTip('Data Management Settings')
        self.dataManagementMenu.triggered.connect(self.dbconnectionwind.show)
        
        toolsMenu = self.menuBar.addMenu('&Tools')
        toolsMenu.addAction(self.dataManagementMenu)
        
        self.viewWindowMenus(self.menuBar, self)

        self.helpMenu = QAction("&Help - SOP", self)
        self.helpMenu.setShortcut("Ctrl+h")
        self.helpMenu.setStatusTip('Help')
        self.helpMenu.triggered.connect(self.weblinks.help)
        self.devBugsMenu = QAction("&Development and Bugs", self)
        self.devBugsMenu.setShortcut("Ctrl+b")
        self.devBugsMenu.setStatusTip('Development and bugs')
        self.devBugsMenu.triggered.connect(self.weblinks.dev)
        self.dataManagMenu = QAction("&Data management", self)
        self.dataManagMenu.setShortcut("Ctrl+m")
        self.dataManagMenu.setStatusTip('Data Management')
        self.dataManagMenu.triggered.connect(self.weblinks.dm)
        self.wikiMenu = QAction("&GridEdge Wiki", self)
        self.wikiMenu.setShortcut("Ctrl+y")
        self.wikiMenu.setStatusTip('GridEdge Wiki')
        self.wikiMenu.triggered.connect(self.weblinks.wiki)
        self.aboutMenu = QAction("&About", self)
        self.aboutMenu = QAction("&About", self)
        self.aboutMenu.setShortcut("Ctrl+a")
        self.aboutMenu.setStatusTip('About')
        self.aboutMenu.triggered.connect(self.aboutwid.show)
        
        aboutMenu = self.menuBar.addMenu('&Help')
        aboutMenu.addAction(self.helpMenu)
        aboutMenu.addSeparator()
        aboutMenu.addAction(self.wikiMenu)
        aboutMenu.addAction(self.devBugsMenu)
        aboutMenu.addAction(self.dataManagMenu)
        aboutMenu.addSeparator()
        aboutMenu.addAction(self.aboutMenu)
        
        # Toolbar Entries #
        self.sampleToolbar = QAction("&Substrates", self)
        self.sampleToolbar.setShortcut("Ctrl+s")
        self.sampleToolbar.setStatusTip('Device Configuration')
        self.sampleToolbar.triggered.connect(self.samplewind.show)
        
        self.acquisitionToolbar = QAction("&Acquisition", self)
        self.acquisitionToolbar.setShortcut("Ctrl+a")
        self.acquisitionToolbar.setStatusTip('Acquisition paramenters')
        self.acquisitionToolbar.triggered.connect(self.acquisitionwind.show)
        
        self.resultsToolbar = QAction("&Results", self)
        self.resultsToolbar.setShortcut("Ctrl+p")
        self.resultsToolbar.setStatusTip('Results Panel')
        self.resultsToolbar.triggered.connect(self.resultswind.show)
        
        self.cameraToolbar = QAction("&Alignment", self)
        self.cameraToolbar.setShortcut("Ctrl+c")
        self.cameraToolbar.setStatusTip('Substrate alignment via Camera')
        self.cameraToolbar.triggered.connect(self.showCameraSample)
        
        #toolBar = self.addToolBar("&Toolbar")
        self.toolBar.addAction(self.sampleToolbar)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.cameraToolbar)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.acquisitionToolbar)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.resultsToolbar)
        self.toolBar.addSeparator()
       
        #### Create status bar ####
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBarLabel = QLabel(self)
        self.statusBar.addPermanentWidget(self.statusBarLabel, 1)
        self.statusBarLabel.setText("System: ready")
        #self.statusBar().showMessage("Ready", 5000)
    
        #### Create basic push buttons to run acquisition ####
        self.startAcqButton = QPushButton(self)
        self.startAcqButton.setGeometry(QRect(10, 110, 160, 50))
        self.startAcqButton.setObjectName("Start Acquisition")
        self.startAcqButton.setText("Start Acquisition")
        self.startAcqButton.clicked.connect(self.acquisition.start)
        self.stopAcqButton = QPushButton(self)
        self.stopAcqButton.setGeometry(QRect(170, 110, 160, 50))
        self.stopAcqButton.setObjectName("Stop Acquisition")
        self.stopAcqButton.setText("Stop Acquisition")
        self.stopAcqButton.setEnabled(False)
        self.stopAcqButton.clicked.connect(self.acquisition.stop)
        self.logo = QLabel(self)
        self.logo.setGeometry(QRect(20, 40, 311, 61))
        self.logo.setText("")
        self.logo.setPixmap(QPixmap(os.path.dirname(__file__)+"/rsrc/logo.png"))
        self.logo.setObjectName("logo")
    
    # Logic for loading parameters from a configuration file
    def loadConfig(self):
        filename = QFileDialog.getOpenFileName(self,
                        "Open INI config file", "","*.ini")
        self.config.readConfig(filename)
        print("Confguration parameters loaded from:",filename[0])
        logger.info("Confguration parameters loaded from:"+filename[0])
    
    # Logic for saving parameters to a configuration file
    def saveConfig(self):
        filename = QFileDialog.getSaveFileName(self,
                        "Save INI config file", "","*.ini")
        self.config.saveConfig(filename[0])
        print("Confguration parameters saved to:",filename[0])
        logger.info("Confguration parameters saved to:"+filename[0])

    # When closing the MainWindow, all windows need to close as we..
    def fileQuit(self):
        QApplication.closeAllWindows()
    
    # Enable/disable buttons
    def enableButtonsAcq(self,flag):
        if flag is False:
            self.startAcqButton.setText("Acquisition Running...")
        else:
            self.startAcqButton.setText("Start Acquisition")
        self.startAcqButton.setEnabled(flag)
        self.stopAcqButton.setEnabled(not flag)

    # Adds Menus to expose other Windows.
    def viewWindowMenus(self, menuObj, obj):
        viewMainWindowMenu = QAction("&Main Window", self)
        viewMainWindowMenu.setShortcut("Ctrl+w")
        viewMainWindowMenu.setStatusTip('Display Main Window')
        viewMainWindowMenu.triggered.connect(lambda: self.displayMainWindow(obj))
        viewSampleMenu = QAction("&Substrates Window", self)
        viewSampleMenu.setShortcut("Ctrl+d")
        viewSampleMenu.setStatusTip('Display Substrates Window')
        viewSampleMenu.triggered.connect(lambda: self.displayMainWindow(obj.samplewind))
        viewCameraMenu = QAction("&Alignment Window", self)
        viewCameraMenu.setShortcut("Ctrl+c")
        viewCameraMenu.setStatusTip('Camera alignment Window')
        viewCameraMenu.triggered.connect(lambda: self.displayMainWindow(obj.camerawind))
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
        windowMenu.addAction(viewCameraMenu)
        windowMenu.addAction(viewAcquisitionMenu)
        windowMenu.addAction(viewResultsMenu)

    # Display main window
    def displayMainWindow(self, obj):
        obj.show()
        obj.setWindowState(obj.windowState() & Qt.WindowMinimized | Qt.WindowActive)
        obj.raise_()
        obj.activateWindow()
    
    # Open both Powermeter and stage windows when calling the Powermeter menu
    # This is to facilitate positioning of the stage with the solar sim over the powermeter
    def showPowermeterShutter(self):
        self.powermeterwind.show()
        self.stagewind.show()
    
    # Open both Sample and Camera windows when calling the Camera alignment menu
    # This is to facilitate checking ofr the alignment status for each substrate listed
    def showCameraSample(self):
        self.camerawind.show()
        self.samplewind.show()

    # Logic to run when quitting the program
    # Dialog box for confirmation
    def closeEvent(self, event):
        quit_msg = "Are you sure you want to exit the program?"
        reply = QMessageBox.question(self, 'Message',
                     quit_msg, QMessageBox.No, QMessageBox.Yes)

        if reply == QMessageBox.Yes:
            if self.stagewind.activeStage == True:
                self.stagewind.activateStage()
            if hasattr(self.acquisition,"acq_thread"):
                self.acquisition.acq_thread.stop()
            self.camerawind.alignOn=False
            self.camerawind.firstRun=False
            self.close()
            self.fileQuit()
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
        #webbrowser.open("https://sites.google.com/site/gridedgesolar/")
        webbrowser.open("https://docs.google.com/document/d/13y0wFV21d75kd37jS3CpJvZL-_ImOJHvAZBCXCPn-OQ/edit")
    def dev(self):
        webbrowser.open("https://github.mit.edu/GridEdgeSolar/Autotesting")
    def dm(self):
        webbrowser.open("http://gridedgedm.mit.edu")
    def wiki(self):
        webbrowser.open("https://sites.google.com/site/gridedgesolar/home")

'''
   About Widget
   Definition of About Panel
'''
class AboutWidget(QWidget):
    """ PyQt widget for About Box Panel """
    
    def __init__(self):
        super(AboutWidget, self).__init__()
        self.initUI()
    
    # Define UI elements
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
        self.logo.setPixmap(QPixmap(os.path.dirname(__file__)+"/rsrc/logo_about.png"))
        self.logo.setObjectName("logo")

        self.labelTitle = QLabel("<qt><b><big><a href = http://gridedgesolar.com>Autotesting %s</a></b></big></qt>" % __version__, self)
        self.labelBy = QLabel("by: %s" % __author__, self)
        self.labelContact = QLabel("<qt>Contact: <a href = mailto:mitgridedge@gmail.com> mitgridedge@gmail.com</a></qt>", self)
        self.labelDetails = QLabel("<a href = http://gridedgesolar.com>GridEdgeSolar </a>is a Solar PV project at <a href = http://mit.edu> MIT</a>", self)
        self.labelLicense = QLabel("This software is licensed under the <a href = https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html> GNU GPL v.2.0 or later</a>", self)
        
        for label in [self.logo, self.labelTitle, self.labelBy,
                self.labelContact, self.labelDetails, self.labelLicense]:
            label.setWordWrap(True)
            label.setOpenExternalLinks(True);
            self.verticalLayout.addWidget(label)
