'''
cameraWindow.py
---------------
Class for providing a graphical user interface
for the cameraWindow

Copyright (C) 2017 Nicola Ferralis <ferralis@mit.edu>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

'''
import sys
from datetime import datetime
from PyQt5.QtWidgets import (QMainWindow, QPushButton, QAction,
    QVBoxLayout,QLabel,QGraphicsView,QFileDialog,QStatusBar,
    QGraphicsScene, QLineEdit,QMessageBox,QWidget,QApplication,
    QGraphicsRectItem,QGraphicsItem,QToolBar)
from PyQt5.QtGui import (QIcon,QImage,QKeySequence,QPixmap,QPainter,
                         QBrush,QColor,QTransform,QPen)
from PyQt5.QtCore import (pyqtSlot,QRectF,QPoint,QRect,Qt,QPointF)

from .modules.camera.camera import *
from .configuration import *
from .acquisition import *
from .modules.xystage.xystage import *
from . import logger

'''
   Camera Window
'''
class CameraWindow(QMainWindow):
    def __init__(self, parent=None):
        super(CameraWindow, self).__init__(parent)
        self.initUI()
        self.config = Configuration()
        self.config.readConfig(self.config.configFile)
        self.numRow = self.config.numSubsHolderRow
        self.numCol = self.config.numSubsHolderCol
    
    def initUI(self):
        # Set up Window geometry and shape
        self.setGeometry(480, 500, 700, 480)
        self.setWindowTitle('Camera Panel')
        # Set up status bar
        self.statusBar().showMessage("Camera: Ready", 5000)
        
        # Set up Graphic Scene and View
        self.scene = GraphicsScene(self)
        self.view = GraphicsView()
        self.view.setScene(self.scene)
        self.view.setMinimumSize(660, 480)
        self.imageLabel = QLabel()
        #self.setCentralWidget(self.imageLabel)
        self.setCentralWidget(self.view)
        self.image_data = None
        
        self.begin = QPoint()
        self.end = QPoint()
        self.firstTimeRunning = True
        
        # Set up ToolBar
        tb = self.addToolBar("Controls")
        tb2 =  QToolBar(self)
        tb2.setGeometry(0,480,660,25)
        
        self.updateBtn = QAction(QIcon(QPixmap()),"Get Camera Image",self)
        self.updateBtn.setShortcut('Ctrl+c')
        self.updateBtn.setStatusTip('Get camera feed, set integration window')
        
        self.liveFeedBtn = QAction(QIcon(QPixmap()), "Live Feed",self)
        self.liveFeedBtn.setShortcut('Ctrl+d')
        self.liveFeedBtn.setStatusTip('Set Default Alignment')
        self.liveFeedBtn.setEnabled(True)
        
        self.manualAlignBtn = QAction(QIcon(QPixmap()),"Check Alignment Manually",self)
        self.manualAlignBtn.setEnabled(False)
        self.manualAlignBtn.setShortcut('Ctrl+m')
        self.manualAlignBtn.setStatusTip('Check Alignment Manually')
        
        self.autoAlignBtn = QAction(QIcon(QPixmap()),"Run Automated Alignment",self)
        self.autoAlignBtn.setEnabled(True)
        self.autoAlignBtn.setShortcut('Ctrl+r')
        self.autoAlignBtn.setStatusTip('Run Automated Alignment Routine')
        
        contrastAlignLabel = QLabel()
        contrastAlignLabel.setText("Current alignment [%]: ")
        self.checkAlignText = QLineEdit()
        self.checkAlignText.setMaximumSize(50, 25)
        self.checkAlignText.setReadOnly(True)
        
        self.setDefaultBtn = QAction(QIcon(QPixmap()),
                                     "Set Default Alignment",self)
        self.setDefaultBtn.setShortcut('Ctrl+d')
        self.setDefaultBtn.setStatusTip('Set Default Alignment')
        self.setDefaultBtn.setEnabled(False)

        tb.addAction(self.autoAlignBtn)
        tb.addSeparator()
        tb.addSeparator()
        tb.addAction(self.updateBtn)
        tb.addSeparator()
        tb.addAction(self.liveFeedBtn)
        tb.addSeparator()
        tb.addAction(self.manualAlignBtn)
        tb.addSeparator()

        
        tb2.addWidget(contrastAlignLabel)
        tb2.addWidget(self.checkAlignText)
        self.checkAlignText.show()
        tb2.addSeparator()
        tb2.addAction(self.setDefaultBtn)
        tb2.addSeparator()
        
        self.autoAlignBtn.triggered.connect(self.autoAlign)
        self.manualAlignBtn.triggered.connect(self.manualAlign)
        self.updateBtn.triggered.connect(lambda: self.cameraFeed(False))
        self.setDefaultBtn.triggered.connect(self.setDefault)
        self.liveFeedBtn.triggered.connect(lambda: self.cameraFeed(True))

    # Handle the actual alignment substrate by substrate
    def autoAlign(self):
        performAlignment = False
        for j in range(self.numCol):
            for i in range(self.numRow):
                if self.parent().samplewind.tableWidget.item(i,j).text() != "":
                    performAlignment = True
        if performAlignment == False:
            self.noSubstratesMessageBox()
            return
        
        self.autoAlignBtn.setEnabled(False)
        self.printMsg("Activating XY stage for automated alignment...")
        self.xystage = XYstage()
        if self.xystage.xystageInit == False:
            self.printMsg(" Stage not activated: automated acquisition not possible. Aborting.")
            self.autoAlignBtn.setEnabled(True)
            return
        self.printMsg(" Stage activated.")

        self.firstRun = True
        for j in range(self.numCol):
            for i in range(self.numRow):
                # Convert to correct substrate number in holder
                substrateNum = Acquisition().getSubstrateNumber(i,j)
                
                # Check if the holder has a substrate in that slot
                if self.parent().samplewind.tableWidget.item(i,j).text() != ""  and \
                        self.parent().samplewind.activeSubs[i,j] == True:
                    self.parent().samplewind.colorCellAcq(i,j,"yellow")
                                        
                    # Move stage to desired substrate
                    if self.xystage.xystageInit is True:
                        self.printMsg("Moving stage to substrate #"+ \
                                        str(substrateNum) + \
                                        ": ("+str(i+1)+", "+str(j+1)+")")
                        self.xystage.move_to_substrate_4x4(substrateNum)
                        time.sleep(0.1)
                        
                        self.cameraFeed(False)
                        while self.firstRun:
                            self.printMsg(" press SPACE to continue with the alignment")
                    
                        alignFlag, alignPerc, iMax = self.alignment()
                        
                        if float(alignPerc) > self.config.alignmentContrastDefault \
                                    and float(iMax) > self.config.alignmentIntMax:
                                self.parent().samplewind.colorCellAcq(i,j,"grey")
                                self.printMsg("Substrate #"+str(substrateNum)+" not aligned! (alignPerc = "+ str(alignPerc)+")")
                        else:
                                self.parent().samplewind.colorCellAcq(i,j,"white")
                                self.printMsg("Substrate #"+str(substrateNum)+" aligned (alignPerc = "+ str(alignPerc)+")")

                else:
                    self.printMsg(" No substrate entered in Substrate Window. Aborting alignment" )
                                
        self.Msg.emit("Deactivating Stage...")
        self.xystage.end_stage_control()
        del self.xystage
        self.printMsg("Stage deactivated")
        self.autoAlignBtn.setEnabled(True)

    # Manually check the alignment
    def manualAlign(self):
        self.updateBtn.setText("Get Camera Image")
        self.liveFeedBtn.setText("Live Feed")
        
        alignFlag, alignPerc, iMax = self.alignment()
        
        if float(alignPerc) > self.config.alignmentContrastDefault \
                and float(iMax) > self.config.alignmentIntMax:
            self.outAlignmentMessageBox()
        else:
            self.printMsg(" Devices and masks appear to be correct")
            
    # Alignment routine
    def alignment(self):
        image, image_data, image_orig = self.cam.get_image(True,
                             int(self.initial.x()),
                             int(self.final.x()),
                             int(self.initial.y()),
                             int(self.final.y()))
                
        alignPerc, iMax = self.cam.check_alignment( \
                image_data,
                self.config.alignmentIntThreshold)

        self.checkAlignText.setText(str(alignPerc))
        if float(alignPerc) > self.config.alignmentContrastDefault \
                and float(iMax) > self.config.alignmentIntMax:
            self.checkAlignText.setStyleSheet("color: rgb(255, 0, 255);")
            return False, alignPerc, iMax
        else:
            return True, alignPerc, iMax

    # Get image from feed
    def cameraFeed(self, live):
        self.cam = CameraFeed()
        self.setDefaultBtn.setEnabled(True)
        try:
            self.checkAlignText.setStyleSheet("color: rgb(0, 0, 0);")
            if live:
                self.liveFeedBtn.setText("Set integration window")
                self.updateBtn.setEnabled(False)
                QApplication.processEvents()
                self.img = self.cam.grab_image_live()
            else:
                self.updateBtn.setText("Set integration window")
                self.liveFeedBtn.setEnabled(False)
                QApplication.processEvents()
                self.img = self.cam.grab_image()
            self.image, self.image_data, temp = self.cam.get_image(False,0,0,0,0)
            
            pixMap = QPixmap.fromImage(self.image)
            self.scene.addPixmap(pixMap)
            #self.imageLabel.setPixmap(QPixmap.fromImage(self.image))
            self.view.fitInView(self.view.sceneRect(), Qt.KeepAspectRatio)

            self.statusBar().showMessage('Camera-feed' + \
                 str(datetime.now().strftime(' (%Y-%m-%d %H-%M-%S)')), 5000)
            self.statusBar().showMessage(' Drag Mouse to select area for alignment', 5000)
            self.liveFeedBtn.setEnabled(True)
            self.updateBtn.setEnabled(True)
        except:
            self.statusBar().showMessage(' USB camera not connected', 5000)

    # Set default values for alignment parameters
    def setDefault(self):
        try:
            self.setDefaultMessageBox(self.alignPerc)
            self.statusBar().showMessage(' Set default:' + self.alignPerc, 5000)
        except:
            self.statusBar().showMessage(' Acquire image first', 5000)

    # Dialog box and logic to set new alignment parameters.
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
            self.parent().config.conf['Instruments']['alignmentContrastDefault'] = str(self.alignPerc)
            self.parent().config.conf['Instruments']['alignmentIntMax'] = str(self.iMax)
            with open(self.parent().config.configFile, 'w') as configfile:
                self.parent().config.conf.write(configfile)
            self.parent().config.readConfig(self.parent().config.configFile)
            self.printMsg(" New alignment settings saved as default. Image saved in: "+self.filename)
            self.cam.save_image(self.parent().config.imagesFolder+self.filename)
            return True
        else:
            self.printMsg( " Alignment settings not saved as default")
            return False

    # Warning box for misalignment
    def outAlignmentMessageBox(self):
        msgBox = QMessageBox( self )
        msgBox.setIcon( QMessageBox.Information )
        msgBox.setText( "WARNING: devices and mask might be misaligned " )
        msgBox.setInformativeText( "Please realign and retry" )
        msgBox.exec_()

    # No substrate selected box
    def noSubstratesMessageBox(self):
        msgBox = QMessageBox( self )
        msgBox.setIcon( QMessageBox.Information )
        msgBox.setText( "WARNING: No substrates selected " )
        msgBox.setInformativeText( "Please add the substrates in the substrate window" )
        msgBox.exec_()
    
    # Show message on log and terminal
    def printMsg(self, msg):
        print(msg)
        self.statusBar().showMessage(msg)
        logger.info(msg)

    # Close camera feed upon closing window.
    def closeEvent(self, event):
        if hasattr(self,"cam"):
            self.cam.closeLiveFeed = True
            #self.firstTimeRunning = True
            del self.cam
        self.scene.cleanup()

'''
   QGraphicsSelectionItem
   Definition of the class to generate the rectangular selection
'''
class QGraphicsSelectionItem(QGraphicsRectItem):
    
    # Class defining Rectangular Selection
    def __init__(self, initPos, finalPos, parent=None):
        super(QGraphicsSelectionItem, self).__init__(parent)
        self.setRect(QRectF(initPos, finalPos))
        self.setPen(QPen(Qt.blue))
        self.setFlags(self.flags() |
                      QGraphicsItem.ItemIsSelectable|
                      QGraphicsItem.ItemIsFocusable)
'''
   GraphicsView
   Custom GraphicsView to display the scene
'''
class GraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super(GraphicsView, self).__init__(parent)
        self.setRenderHints(QPainter.Antialiasing)
    
    # Resize image when resizing cameraWindow
    def resizeEvent(self, event):
        self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)
    
    def drawBackground(self, painter, rect):
        painter.fillRect(rect, QBrush(Qt.lightGray))
        self.scene().drawBackground(painter, rect)

'''
   GraphicsScene
   Custom GraphicScene having all the main content.
'''
class GraphicsScene(QGraphicsScene):

    def __init__(self, parent=None):
        super(GraphicsScene, self).__init__(parent)

    # Create rectangular selection
    def addRect(self):
        self.removeRectangles()
        item = QGraphicsSelectionItem(self.parent().begin,self.parent().end)
        self.clearSelection()
        self.addItem(item)
        item.setSelected(True)
        self.setFocusItem(item)
        #item.setToolTip(self.spotsLabel[-1])
        self.update()

    # Mouse event driven routines for generating rectangular selections
    def mousePressEvent(self, event):
        if len(self.items()) !=0:
            self.removeRectangles()
        if event.button() == Qt.LeftButton:
            self.parent().begin = event.scenePos()
            self.parent().initial = event.scenePos()
            self.update()

    def mouseMoveEvent(self, event):
        if len(self.items()) !=0:
            self.parent().end = event.scenePos()
            self.addRect()
    
    # Rectangular selection is
    def mouseReleaseEvent(self, event):
        self.parent().end = event.scenePos()
        self.parent().final = event.scenePos()
        self.parent().update()
        try:
            if len(self.items()) !=0:
                self.addRect()
            self.parent().manualAlignBtn.setEnabled(True)
            self.parent().statusBar().showMessage(' Press SPACE to set Rectangular Selection', 5000)
        except:
            pass

    # keyboard event driven routines for fixing the selection for analysis
    def keyPressEvent(self, event):
        if len(self.items())>1:
            if event.key() == Qt.Key_Space:
                #self.parent().manualAlign()
                self.parent().firstRun = False
                self.parent().printMsg(" Continuing alignment...")
    
    # Remove rectangular selections upon redrawing, leave image
    def removeRectangles(self):
        """ Remove all spots from the scene (leaves background unchanged). """
        if len(self.items()) == 1 :
            self.image_item = self.items()[0]
        for item in self.items():
            self.removeItem(item)
        self.addItem(self.image_item)
        self.update

    # cleaup scene and view
    def cleanup(self):
        try:
            for item in self.items():
                self.removeItem(item)
            self.update
            del self.image
            del self.image_data
            del self.image_orig
        except:
            pass

    '''
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
    '''




