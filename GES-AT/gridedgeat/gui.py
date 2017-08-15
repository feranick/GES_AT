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

import sys, webbrowser, random
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
from .acquisitionWindow import *

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
        self.setGeometry(10,30,300,200)
        self.aboutwid = AboutWidget()
        self.samplewind = SampleWindow()
        self.acquisitionwind = AcquisitionWindow()
        self.resultswind = ResultsWindow()
        self.camerawind = CameraWindow()
        self.weblinks = WebLinksWidget()
     
        #### define actions ####
        # actions for "File" menu
        #self.fileOpenAction = self.createAction("&Open...", self.camerawind.fileOpen,
        #        QKeySequence.Open, None,
        #        "Open a directory containing the image files.")
        self.fileQuitAction = self.createAction("&Quit", self.fileQuit,
                QKeySequence("Ctrl+q"), None,
                "Close the application.")
        self.fileActions = [None, self.fileQuitAction]
                
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
        self.helpActions = [None, self.helpAction, None, self.aboutAction,
                None, self.devAction]
                
        #### Create menu bar ####
        fileMenu = self.menuBar().addMenu("&File")
        self.addActions(fileMenu, self.fileActions)
        #processMenu = self.menuBar().addMenu("&Process")
        #self.addActions(processMenu, self.processActions)
        #self.enableProcessActions(False)
        helpMenu = self.menuBar().addMenu("&Help")
        self.addActions(helpMenu, self.helpActions)
                
        #### define actions ####
        # actions for "Buttons" menu
        self.SampleAction = self.createAction("&Sample", self.samplewind.show,
                QKeySequence("Ctrl+s"), None,
                "Sample panel")
        self.AcquisitionAction = self.createAction("&Acquisition", self.acquisitionwind.show,
                QKeySequence("Ctrl+r"), None,
                "Acquisition Setup panel")
        self.ResultsAction = self.createAction("&Results", self.resultswind.show,
                QKeySequence("Ctrl+p"), None,
                "Results panel")
        self.CameraAction = self.createAction("&Camera", self.camerawind.show,
                QKeySequence("Ctrl+c"), None,
                "Camera panel")
    
    
        #### Create tool bar ####
        toolBar = self.addToolBar("&Toolbar")
        # adding actions to the toolbar, addActions-function creates a separator with "None"
        self.toolBarActions = [self.SampleAction, None, self.AcquisitionAction, None, self.ResultsAction, None,
                               self.CameraAction, None]
        self.addActions(toolBar, self.toolBarActions)
        
        #### Create status bar ####
        self.statusBar().showMessage("Ready", 5000)
    
        #### Create basic push buttons to run acquisition ####
        self.startAcqButton = QPushButton(self)
        self.startAcqButton.setGeometry(QRect(10, 30, 150, 50))
        self.startAcqButton.setObjectName("Start Acquisition")
        self.startAcqButton.setText("Start Acquisition")
        self.stopAcqButton = QPushButton(self)
        self.stopAcqButton.setGeometry(QRect(10, 85, 150, 50))
        self.stopAcqButton.setObjectName("Stop Acquisition")
        self.stopAcqButton.setText("Stop Acquisition")



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
        self.setGeometry(100, 200, 400, 200)
        self.setWindowTitle('About GridEdge AutoTesting')
    
        self.gridLayout = QGridLayout()
        self.setLayout(self.gridLayout)
        self.verticalLayout = QVBoxLayout()
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.labelTitle = QLabel("<qt><b><big><a href = http://gridedgesolar.com>GridEdgeSolar %s</a></b></big></qt>" % __version__, self);
        self.labelBy = QLabel("by: %s" % __author__, self)
        self.labelContact = QLabel("<qt>Contacts: <a href = mailto:mitgridedge@gmail.com> mitgridedge@gmail.com</a></qt>", self)
        self.labelDetails = QLabel("GridEdgeSolar is a Solar PV project at MIT ", self)
        self.labelPaper = QLabel("<qt> GridEdgeSolar", self)
        for label in [self.labelTitle, self.labelBy, self.labelContact, self.labelDetails, self.labelPaper]:
            label.setWordWrap(True)
            label.setOpenExternalLinks(True);
            self.verticalLayout.addWidget(label)

