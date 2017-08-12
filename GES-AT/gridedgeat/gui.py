'''
gui.py
-------------
Various classes for providing a graphical user interface.
'''

import sys, webbrowser
from datetime import datetime
from .qt.widgets import (QMainWindow, QApplication, QPushButton, QWidget, QAction,
    QVBoxLayout,QGridLayout,QLabel,QGraphicsView,QKeySequence,QFileDialog,QStatusBar,
    QPixmap,QGraphicsScene,QPainter,QLineEdit,QMessageBox)
from .qt.QtGui import (QIcon,QImage)
from .qt.QtCore import (pyqtSlot,QRectF)
from .qt import qt_filedialog_convert

from . import config
from . import __version__
from . import __author__
from .camera import *

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
        self.setGeometry(config.InMainWindowWidth, config.InMainWindowHeight,
            config.FinMainWindowWidth, config.FinMainWindowHeight)
        self.aboutwid = AboutWidget()
        self.acquisitionwind = AcquisitionWindow()
        self.plotwind = PlotWindow()
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
        self.AcquisitionAction = self.createAction("&Acquisition", self.acquisitionwind.show,
                QKeySequence("Ctrl+r"), None,
                "Acquisition panel")
        self.PlotAction = self.createAction("&Plots", self.plotwind.show,
                QKeySequence("Ctrl+p"), None,
                "Plotting panel")
        self.CameraAction = self.createAction("&Camera", self.camerawind.show,
                QKeySequence("Ctrl+c"), None,
                "Camera panel")
    
    
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
        self.cam = CameraFeed()
        self.initUI()
    
    def initUI(self):
        # Set up Window geometry and shape
        self.setGeometry(100, 500, 660, 480)
        self.setWindowTitle('Camera Panel')
        # Set up status bar
        self.statusBar().showMessage("Camera: Ready", 5000)
        
        # Set up Graphic Scene and View
        self.scene = GraphicsScene(self)
        self.view = GraphicsView()
        self.view.setScene(self.scene)
        self.view.setMinimumSize(660, 480)
        self.imageLabel = QLabel()
        self.setCentralWidget(self.imageLabel)
        # Set Camera Feed and calculate contrast
        #self.cameraFeed()
        
        # Set up ToolBar
        tb = self.addToolBar("Camera")
        updateBtn = QAction(QIcon(QPixmap()),"Update Camera Feed",self)
        updateBtn.setShortcut('Ctrl+c')
        updateBtn.setStatusTip('Get Camera Feed')
        tb.addAction(updateBtn)
        tb.addSeparator()
        
        contrastAlignLabel = QLabel()
        contrastAlignLabel.setText("Check alignment [%]: ")
        tb.addWidget(contrastAlignLabel)
        self.checkAlignText = QLineEdit()
        self.checkAlignText.setMaximumSize(50, 25)
        self.checkAlignText.setReadOnly(True)
        tb.addWidget(self.checkAlignText)
        self.checkAlignText.show()
        tb.addSeparator()
        
        setDefaultBtn = QAction(QIcon(QPixmap()),"Set Default Alignment",self)
        setDefaultBtn.setShortcut('Ctrl+d')
        setDefaultBtn.setStatusTip('Set Default Alignment')
        tb.addAction(setDefaultBtn)
        tb.addSeparator()

        tb.actionTriggered[QAction].connect(self.toolbtnpressed)
    
    def toolbtnpressed(self,a):
        if a.text() == "Update Camera Feed":
            self.cameraFeed()
        if a.text() == "Set Default Alignment":
            self.setDefault()

    def cameraFeed(self):
        try:
            self.checkAlignText.setStyleSheet("color: rgb(0, 0, 0);")
            self.cam.grab_image()
            self.image = self.cam.get_image()
            self.imageLabel.setPixmap(QPixmap.fromImage(self.image))
            self.statusBar().showMessage(self.cam.color_image_name() + \
                str(datetime.now().strftime(' (%Y-%m-%d %H-%M-%S)')), 5000)
            self.alignPerc = str(self.cam.check_alignment(config.cameraAlignmentThreshold))
            self.checkAlignText.setText(self.alignPerc)
            if float(self.alignPerc) > float(config.cameraAlignmentDefault):
                self.checkAlignText.setStyleSheet("color: rgb(255, 0, 255);")
                self.outAlignmentMessageBox()
            else:
                self.statusBar().showMessage(' Devices and masks appear to be correct', 5000)
        except:
            self.statusBar().showMessage(' USB camera not connected', 5000)

    def setDefault(self):
        #try:
        self.setDefaultMessageBox(self.alignPerc)
        self.statusBar().showMessage(' Set default:' + self.alignPerc, 5000)
        #except:
        #    self.statusBar().showMessage(' Acquire image first', 5000)


    def setDefaultMessageBox(self, value):
        msgBox = QMessageBox( self )
        msgBox.setIcon( QMessageBox.Information )
        msgBox.setText( "By changing the default value, you will erase the previous value" )

        msgBox.setInformativeText( "Would you like to set " + value +  " as default?" )
        msgBox.addButton( QMessageBox.Yes )
        msgBox.addButton( QMessageBox.No )

        msgBox.setDefaultButton( QMessageBox.No )
        ret = msgBox.exec_()

        if ret == QMessageBox.Yes:
            self.filename = "calib"+str(datetime.now().strftime('_%Y%m%d_%H-%M-%S.png'))
            print( "Yes", self.filename)
            self.cam.save_image(self.filename)
            return
        else:
            print( "No" )
            return

    def outAlignmentMessageBox(self):
        msgBox = QMessageBox( self )
        msgBox.setIcon( QMessageBox.Information )
        msgBox.setText( "WARNING: devices and mask might be misaligned " )
        msgBox.setInformativeText( "Please realign and retry" )
        msgBox.exec_()

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
   GraphicsScene
   Definition of the View for Camera
'''
class GraphicsScene(QGraphicsScene):
    """ Custom GraphicScene having all the main content."""

    def __init__(self, parent=None):
        super(GraphicsScene, self).__init__(parent)
    
    def drawBackground(self, painter, rect):
        """ Draws image in background if it exists. """
        if hasattr(self, "image"):
            painter.drawImage(QPoint(0, 0), self.image)

    def setBackground(self, image, labeltext):
        """ Sets the background image. """
        if not hasattr(self, 'imlabel'):
            self.imlabel = QGraphicsSimpleTextItem(labeltext)
            self.imlabel.setBrush(QBrush(Qt.white))
            self.imlabel.setPos(5, 5)
        if not hasattr(self,"image") or len(self.items()) < 1:
            self.addItem(self.imlabel)
        self.imlabel.setText(labeltext)
        self.image = image
        self.update()


