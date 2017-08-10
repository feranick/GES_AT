"""
gui.py
-------------

Various classes for providing a graphical user interface.
"""

import sys, webbrowser
from .qt.widgets import (QMainWindow, QApplication, QPushButton, QWidget, QAction,
    QTabWidget,QVBoxLayout,QGridLayout,QLabel)
from .qt.QtGui import QIcon
from .qt.QtCore import pyqtSlot

from . import config
from . import __version__
from . import __author__

class MainWindow(QMainWindow):
 
    def __init__(self):
        super().__init__()
        self.title = 'GridEdge AT - Basic Tabs'
        self.left = 0
        self.top = 0
        self.width = 300
        self.height = 200
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.aboutwid = AboutWidget()
        self.weblinks = WebLinksWidget()

        self.table_widget = MyTableWidget(self)
        self.setGeometry(10, 30, 660, 480)
        self.setCentralWidget(self.table_widget)
 
        self.show()
    
        #### define actions ####
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
        #fileMenu = self.menuBar().addMenu("&File")
        #self.addActions(fileMenu, self.fileActions)
        #processMenu = self.menuBar().addMenu("&Process")
        #self.addActions(processMenu, self.processActions)
        #self.enableProcessActions(False)
        helpMenu = self.menuBar().addMenu("&Help")
        self.addActions(helpMenu, self.helpActions)

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
        self.labelContact = QLabel("<qt>Contacts: <a href = mailto:feranick@hotmail.com> feranick@hotmail.com</a></qt>", self)
        self.labelDetails = QLabel("If GridEdgeSolar is a Solar PV project at MIT ", self)
        self.labelPaper = QLabel("<qt> GridEdgeSolar", self)
        for label in [self.labelTitle, self.labelBy, self.labelContact, self.labelDetails, self.labelPaper]:
            label.setWordWrap(True)
            label.setOpenExternalLinks(True);
            self.verticalLayout.addWidget(label)

class WebLinksWidget():
    def __init__(self):
        super(WebLinksWidget, self).__init__()

    def help(self):
        webbrowser.open("https://sites.google.com/site/gridedgesolar/")
    def dev(self):
        webbrowser.open("https://github.mit.edu/GridEdgeSolar/Autotesting")


class MyTableWidget(QWidget):        
 
    def __init__(self, parent):   
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
 
        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tab1 = QWidget()	
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.tabs.resize(300,400)
 
        # Add tabs
        self.tabs.addTab(self.tab1,"Main")
        self.tabs.addTab(self.tab2,"Plots")
        self.tabs.addTab(self.tab3,"Camera")
 
        self.tab1.layout = QVBoxLayout(self)
        self.pushButton1 = QPushButton("Button")
        self.tab1.layout.addWidget(self.pushButton1)
        self.tab1.setLayout(self.tab1.layout)
 
        # Add tabs to widget        
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

