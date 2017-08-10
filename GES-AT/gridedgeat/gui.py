'''
gui.py
-------------
Various classes for providing a graphical user interface.
'''

import sys, webbrowser
from .qt.widgets import (QMainWindow, QApplication, QPushButton, QWidget, QAction,
    QVBoxLayout,QGridLayout,QLabel,QGraphicsView,QKeySequence,QFileDialog,QStatusBar)
from .qt.QtGui import QIcon
from .qt.QtCore import pyqtSlot
from .qt import qt_filedialog_convert

from . import config
from . import __version__
from . import __author__

'''
   Main Window
   Definition of Main Panel
'''
class MainWindow(QMainWindow):
 
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GridEdge AutoTesting %s" % __version__)
        self.setGeometry(config.InMainWindowWidth, config.InMainWindowHeight,
            config.FinMainWindowWidth, config.FinMainWindowHeight)
        self.aboutwid = AboutWidget()
        self.acquisitionwind = AcquisitionWindow()
        self.plotwind = PlotWindow()
        self.camerawind = CameraWindow()
        self.weblinks = WebLinksWidget()
 
        #self.show()
    
        #### define actions ####
        # actions for "File" menu
        self.fileOpenAction = self.createAction("&Open...", self.camerawind.fileOpen,
                QKeySequence.Open, None,
                "Open a directory containing the image files.")
        self.fileQuitAction = self.createAction("&Quit", self.fileQuit,
                QKeySequence("Ctrl+q"), None,
                "Close the application.")
        self.fileActions = [None, self.fileOpenAction, None, self.fileQuitAction]
                
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
                
        #### define actions ####
        # actions for "File" menu
        self.AcquisitionAction = self.createAction("&Acquisition", self.acquisitionwind.show,
                QKeySequence("Ctrl+r"), None,
                "Acquisition panel")
        self.PlotAction = self.createAction("&Plots", self.plotwind.show,
                QKeySequence("Ctrl+p"), None,
                "Plotting panel")
        self.CameraAction = self.createAction("&Camera", self.camerawind.show,
                QKeySequence("Ctrl+c"), None,
                "Camera panel")
    
        #### Create menu bar ####
        fileMenu = self.menuBar().addMenu("&File")
        self.addActions(fileMenu, self.fileActions)
        #processMenu = self.menuBar().addMenu("&Process")
        #self.addActions(processMenu, self.processActions)
        #self.enableProcessActions(False)
        helpMenu = self.menuBar().addMenu("&Help")
        self.addActions(helpMenu, self.helpActions)
    
        #### Create tool bar ####
        toolBar = self.addToolBar("&Toolbar")
        # adding actions to the toolbar, addActions-function creates a separator with "None"
        self.toolBarActions = [self.AcquisitionAction, None, self.PlotAction, None,
                               self.CameraAction, None]
        self.addActions(toolBar, self.toolBarActions)
        
        #### Create status bar ####
        self.statusBar().showMessage("Ready", 5000)


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
   GraphicsView
   Definition of the View for Camera
'''
class GraphicsView(QGraphicsView):
    """ Custom GraphicsView to display the scene. """
    def __init__(self, parent=None):
        super(GraphicsView, self).__init__(parent)
        self.setRenderHints(QPainter.Antialiasing)
    
    def resizeEvent(self, event):
        self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)
    
    def drawBackground(self, painter, rect):
        painter.fillRect(rect, QBrush(Qt.lightGray))
        self.scene().drawBackground(painter, rect)

'''
   Acquisition Window
'''
class AcquisitionWindow(QMainWindow):
    def __init__(self):
        super(AcquisitionWindow, self).__init__()
        self.initUI()
    
    def initUI(self):
        self.setGeometry(100, 100, 400, 400)
        self.setWindowTitle('Acquisition Panel')
        self.statusBar().showMessage("Acquisition: Ready", 5000)

'''
   Plot Window
'''
class PlotWindow(QMainWindow):
    def __init__(self):
        super(PlotWindow, self).__init__()
        self.initUI()
    
    def initUI(self):
        self.setGeometry(500, 100, 400, 400)
        self.setWindowTitle('Plot Panel')
        self.statusBar().showMessage("Plotting: Ready", 5000)

'''
   Camera Window
'''
class CameraWindow(QMainWindow):
    def __init__(self):
        super(CameraWindow, self).__init__()
        self.initUI()
    
    def initUI(self):
        self.setGeometry(100, 500, 400, 400)
        self.setWindowTitle('Camera Panel')
        self.statusBar().showMessage("Camera: Ready", 5000)

    def fileOpen(self):
        self.show()
        self.statusBar().showMessage("Not implemented yet")

        """
        try:
            files = qt_filedialog_convert(QFileDialog.getOpenFileNames(self,
                    "Open images",
                    filter="Image files (%s)" % (" ".join(AllImageLoader.supported_extensions()))))
            self.loader = AllImageLoader(files, config.IO_energyRegex)
            self.setImage(self.loader.next())
        except IOError as err:
            self.statusBar().showMessage('IOError: ' + str(err), 5000)
        """


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
        self.labelContact = QLabel("<qt>Contacts: <a href = mailto:feranick@hotmail.com> feranick@hotmail.com</a></qt>", self)
        self.labelDetails = QLabel("If GridEdgeSolar is a Solar PV project at MIT ", self)
        self.labelPaper = QLabel("<qt> GridEdgeSolar", self)
        for label in [self.labelTitle, self.labelBy, self.labelContact, self.labelDetails, self.labelPaper]:
            label.setWordWrap(True)
            label.setOpenExternalLinks(True);
            self.verticalLayout.addWidget(label)

