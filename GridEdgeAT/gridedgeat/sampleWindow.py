'''
SampleWindow
------------------
Class for providing a graphical user interface for 
Sample Window

Copyright (C) 2017-2019 Nicola Ferralis <ferralis@mit.edu>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

'''

import sys, re, os.path, time
import numpy as np
from datetime import datetime
from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton,
    QWidget, QAction,QVBoxLayout,QGridLayout,QLabel,QGraphicsView,
    QFileDialog,QStatusBar,QTableWidget,QGraphicsScene,QLineEdit,
    QMessageBox,QDialog,QComboBox,QMenuBar,QDialogButtonBox,
    QAbstractItemView,QTableWidgetItem,QMenu,QListWidget,QHeaderView)
from PyQt5.QtGui import (QIcon,QImage,QKeySequence,QPixmap,QPainter,QColor,
    QCursor)
from PyQt5.QtCore import (Qt,pyqtSlot,QRectF,QRect,QCoreApplication,QSize)

from . import logger
from .configuration import *
from .acquisition import *
from .resultsWindow import *
from .modules.sourcemeter.sourcemeter import *
from .modules.switchbox.switchbox import *

####################################################################
#   Sample Window
####################################################################
class SampleWindow(QMainWindow):
    def __init__(self, parent=None):
        super(SampleWindow, self).__init__(parent)
        self.activeSubs = np.ones((self.parent().config.numSubsHolderRow,
                self.parent().config.numSubsHolderCol),
                dtype=bool)
        self.archSubs = np.zeros((self.parent().config.numSubsHolderRow,
                self.parent().config.numSubsHolderCol),dtype=int)
        self.initUI(self)
    
    # Define UI elements
    def initUI(self,MainWindow):
        self.setGeometry(10, 300, 520, 630)
        self.setFixedSize(self.size())
        MainWindow.setWindowTitle("Substrates configuration")
        
        self.stageImg = QLabel(self)
        self.stageImg.setGeometry(QRect(10, 200, 567, 410))
        self.stageImg.setText("XY Stage")
        self.stageImg.setPixmap(QPixmap(os.path.dirname(__file__)+"/rsrc/stage.jpg"))
        
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayoutWidget = QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QRect(10, 0, 380, 150))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.windowGridLayout = QGridLayout(self.gridLayoutWidget)
        self.windowGridLayout.setContentsMargins(0, 0, 0, 0)
        self.windowGridLayout.setSpacing(1)
        self.windowGridLayout.setObjectName("windowGridLayout")
        
        self.operatorLabel = QLabel(self.gridLayoutWidget)
        self.operatorLabel.setObjectName("operatorLabel")
        self.windowGridLayout.addWidget(self.operatorLabel, 0, 0, 1, 1)
        self.operatorText = QLineEdit(self.gridLayoutWidget)
        self.operatorText.setText("")
        self.operatorText.setObjectName("operatorText")
        self.windowGridLayout.addWidget(self.operatorText, 0, 1, 1, 1)
        
        self.holderTypeCBox = QComboBox(self.gridLayoutWidget)
        self.holderTypeCBox.setObjectName("holderTypeCBox")
        self.windowGridLayout.addWidget(self.holderTypeCBox, 1, 1, 1, 1)
        self.holderTypeLabel = QLabel(self.gridLayoutWidget)
        self.holderTypeLabel.setObjectName("holderTypeLabel")
        self.windowGridLayout.addWidget(self.holderTypeLabel, 1, 0, 1, 1)
        self.holderTypeCBox.addItem(str(self.parent().config.numSubsHolderRow)+\
                                    "x"+str(self.parent().config.numSubsHolderRow))
        self.holderTypeCBox.setEnabled(False)
        
        self.deviceAreaLabel = QLabel(self.gridLayoutWidget)
        self.windowGridLayout.addWidget(self.deviceAreaLabel, 2, 0, 1, 1)
        self.deviceAreaText = QLineEdit(self.gridLayoutWidget)
        self.windowGridLayout.addWidget(self.deviceAreaText, 2, 1, 1, 1)
        self.deviceAreaText.setText(str(self.parent().config.deviceArea))
        self.deviceAreaText.editingFinished.connect(self.setDeviceArea)
        self.deviceAreaText.setEnabled(True)
        
        self.deviceArchLabel = QLabel(self.gridLayoutWidget)
        self.windowGridLayout.addWidget(self.deviceArchLabel, 3, 0, 1, 1)
        self.deviceArchCBox = QComboBox(self.gridLayoutWidget)
        self.deviceArchCBox.setObjectName("deviceArchCBox")
        self.windowGridLayout.addWidget(self.deviceArchCBox, 1, 1, 1, 1)
        self.windowGridLayout.addWidget(self.deviceArchCBox, 3, 1, 1, 1)
        #self.deviceArchCBox.setEnabled(False)
        self.deviceArchCBox.setToolTip("Device architecture will be submitted to the DM along with your data")
        self.populateArchCBox()
        self.deviceArchCBox.currentIndexChanged.connect(lambda: self.setArch(self.deviceArchCBox.currentIndex()))
        
        self.commentsLabel = QLabel(self.centralwidget)
        self.commentsLabel.setObjectName("commentsLabel")
        self.commentsLabel.setGeometry(QRect(10, 150, 80, 20))
        self.commentsText = QLineEdit(self.centralwidget)
        self.commentsText.setText("")
        self.commentsText.setGeometry(QRect(90, 150, 420, 20))
        self.commentsText.setObjectName("commentsText")
       
        self.tableWidget = QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QRect(100, 430, 410, 145))
        self.tableWidget.setColumnCount(self.parent().config.numSubsHolderRow)
        self.tableWidget.setRowCount(self.parent().config.numSubsHolderCol)
        self.tableWidget.setVerticalHeaderLabels(("4","3","2","1"))
        self.tableWidget.setHorizontalHeaderLabels(("4","3","2","1"))
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        self.tableWidget.itemClicked.connect(self.onCellClick)

        self.updateTableTooltips(True)
        self.disableBrokenCells(self.parent().config.brokenCells)
        
        self.checkCellsButton = QPushButton(self.centralwidget)
        self.checkCellsButton.setGeometry(QRect(10, 460, 80, 80))
        self.checkCellsButton.setObjectName("checkSample")
        self.checkCellsButton.clicked.connect(self.checkLoadedCells)
        self.checkCellsButton.setToolTip("Correctly loaded cells will appear in cyan")
        self.checkCellsButton.setEnabled(True)
        
        self.tableWidget.itemClicked.connect(self.onCellClick)
        self.tableWidget.itemChanged.connect(self.checkMatch)
        self.tableWidget.itemDoubleClicked.connect(lambda item: self.resetSingleCellAcq(item))

        # Enable editing by Double Click
        self.tableWidget.setEditTriggers(QAbstractItemView.DoubleClicked)

        self.loadButton = QPushButton(self.centralwidget)
        self.loadButton.setGeometry(QRect(405, 30, 100, 40))
        self.loadButton.setObjectName("loadButton")
        self.loadButton.clicked.connect(self.loadCsvSubstrates)
        self.saveButton = QPushButton(self.centralwidget)
        self.saveButton.setGeometry(QRect(405, 80, 100, 40))
        self.saveButton.setObjectName("saveButton")
        self.saveButton.clicked.connect(self.saveCsvSubstrates)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menuBar = QMenuBar(MainWindow)
        self.menuBar.setGeometry(QRect(0, 0, 774, 22))
        self.menuBar.setObjectName("menubar")
        
        self.loadMenu = QAction("&Load Substrates", self)
        self.loadMenu.setShortcut("Ctrl+o")
        self.loadMenu.setStatusTip('Load substrate names from csv')
        self.loadMenu.triggered.connect(self.loadCsvSubstrates)
        self.saveMenu = QAction("&Save Substrates", self)
        self.saveMenu.setShortcut("Ctrl+s")
        self.saveMenu.setStatusTip('Save substrate names to csv')
        self.saveMenu.triggered.connect(self.saveCsvSubstrates)
        self.clearMenu = QAction("&Clear Substrates", self)
        self.clearMenu.setShortcut("Ctrl+x")
        self.clearMenu.setStatusTip('Clear substrate from table')
        self.clearMenu.triggered.connect(self.clearCells)

        fileMenu = self.menuBar.addMenu('&File')
        fileMenu.addAction(self.loadMenu)
        fileMenu.addAction(self.saveMenu)
        fileMenu.addSeparator()
        fileMenu.addAction(self.clearMenu)

        self.parent().viewWindowMenus(self.menuBar, self.parent())

        MainWindow.setMenuBar(self.menuBar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.operatorLabel.setText("Operator")
        self.holderTypeLabel.setText("Holder type")
        self.deviceAreaLabel.setText("Device area [cm\u00B2]  ")
        self.deviceArchLabel.setText("Device architecture  ")
        self.commentsLabel.setText("Comments")
        self.loadButton.setText("Load")
        self.saveButton.setText("Save")
        self.checkCellsButton.setText("Check\nLoaded\nCells")
        
    # Get architecture configuration files.
    def populateArchCBox(self):
        fileList = os.listdir(self.parent().config.archFolder)
        if len(fileList) == 0 or not any([fname.endswith('.json') for fname in fileList]):
            #for i in range(4):
            try:
                i = 0
                while True:
                    name, entry = self.archSubstrate(i)
                    with open(self.parent().config.archFolder+name+'.json','w') as outfile:
                        json.dump(entry,outfile)
                    i+=1
            except:
                pass
    
        for ind, f in enumerate(sorted(os.listdir(self.parent().config.archFolder))):
            if (os.path.splitext(f)[-1] == ".json"):
                self.deviceArchCBox.addItem(os.path.splitext(f)[0])

    # Set the type of architecture for a selected substrates.
    def setArch(self,txt):
        for item in self.tableWidget.selectedItems():
            self.archSubs[item.row(),item.column()] = txt
            msg = " Setting architecture for substrate #"+\
                  str(Acquisition().getSubstrateNumber(item.row(),item.column()))+\
                  " to: "+self.deviceArchCBox.currentText()
            print(msg)
            logger.info(msg)
        self.updateTableTooltips(False)
    
    # Update ToolTips for the sample Table.
    def updateTableTooltips(self, firstTime):
        # This allows for background coloring of a cell
        for i in range(self.parent().config.numSubsHolderCol):
            for j in range(self.parent().config.numSubsHolderRow):
                if firstTime:
                    self.tableWidget.setItem(i,j,QTableWidgetItem())
                self.tableWidget.item(i,j).setToolTip("Substrate #"+\
                    str(Acquisition().getSubstrateNumber(i,j))+"\nArchitecture: "+\
                self.deviceArchCBox.itemText(self.archSubs[j,i]))

    # Enable right click on substrates for disabling/enabling during acquisition.
    def contextMenuEvent(self, event):
        self.menu = QMenu(self)
        row = self.tableWidget.currentRow()
        col = self.tableWidget.currentColumn()
        try:
            if self.tableWidget.item(row,col).text() != "":
                if self.activeSubs[row,col] == True:
                    selectCellAction = QAction('Disable substrate', self)
                else:
                    selectCellAction = QAction('Enable substrate', self)
                viewDMEntryAction = QAction("&View Entry in Database", self)
                showJsonInfoDMAction = QAction("&Show JSON info from Database", self)
                saveJsonInfoDMAction = QAction("&Save JSON from Database", self)
                removeEntryDMAction = QAction("&Remove Entry from Database", self)
                checkCreateLotDMAction = QAction("&Add substrate to batch DM", self)
                addTagDMAction = QAction("&Add tag to substrate in DM", self)
                setArchDfAcqParamsAction = QAction("&Check DataFrame Acq", self)
                self.menu.addAction(selectCellAction)
                self.menu.addAction(viewDMEntryAction)
                self.menu.addSeparator()
                self.menu.addAction(saveJsonInfoDMAction)
                
                '''
                self.menu.addAction(showJsonInfoDMAction)
                self.menu.addSeparator()
                self.menu.addAction(removeEntryDMAction)
                self.menu.addSeparator()
                self.menu.addAction(checkCreateLotDMAction)
                self.menu.addAction(addTagDMAction)
                self.menu.addSeparator()
                self.menu.addAction(setArchDfAcqParamsAction)
                '''
                
                self.menu.popup(QCursor.pos())
                selectCellAction.triggered.connect(lambda: self.selectCell(row,col))
                viewDMEntryAction.triggered.connect(lambda: self.viewOnDM(self.tableWidget.item(row,col).text()))
                showJsonInfoDMAction.triggered.connect(lambda: self.showJsonInfoDM(self.tableWidget.item(row,col).text()))
                saveJsonInfoDMAction.triggered.connect(lambda: self.saveJsonInfoDM(self.tableWidget.item(row,col).text()))
                removeEntryDMAction.triggered.connect(lambda: self.removeEntryDM(self.tableWidget.item(row,col).text()))
                checkCreateLotDMAction.triggered.connect(lambda: self.checkCreateLotDM(self.tableWidget.item(row,col).text(),row, col))
                addTagDMAction.triggered.connect(lambda: self.addTagDM(self.tableWidget.item(row,col).text(),row, col))
                setArchDfAcqParamsAction.triggered.connect(lambda: self.setArchDfAcqParams(row, col))
        except:
            pass

    # Logic to set correct architecture in dfAqcParams
    def setArchDfAcqParams(self, dfAqcParams, row, col):
        arch = self.deviceArchCBox.itemText(self.archSubs[row,col])
        #dfAqcParams = self.parent().acquisition.getAcqParameters()
        dfAqcParams['DevArchitecture'].replace(to_replace=['0_blank'], value=arch, inplace=True)

    # Logic to disable non-working cells
    def disableBrokenCells(self, brokenCells):
        self.enableAllCells()
        for row,col in brokenCells:
            item = self.tableWidget.item(row, col)
            item.setFlags(Qt.ItemIsEditable)
            self.colorCellAcq(row,col,"grey")
            self.activeSubs[row,col] = False

    # Logic to enable non-working cells
    def enableBrokenCells(self):
        for row,col in brokenCells:
            item = self.tableWidget.item(row, col)
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            self.colorCellAcq(row,col,"white")
            self.activeSubs[row,col] = True

    # Logic to enable all cells in Sample table
    def enableAllCells(self):
        for col in range(self.parent().config.numSubsHolderCol):
            for row in range(self.parent().config.numSubsHolderRow):
                item = self.tableWidget.item(row, col)
                item.setFlags(item.flags() | Qt.ItemIsEditable)
                self.colorCellAcq(row,col,"white")
                self.activeSubs[row,col] = True

    # Logic to set substrate status for acquisition
    def selectCell(self, row,col):
        if self.activeSubs[row,col] == True:
            self.colorCellAcq(row,col,"red")
            self.activeSubs[row,col] = False
        else:
            self.colorCellAcq(row,col,"white")
            self.activeSubs[row,col] = True
    
    # Logic to set color in table
    @pyqtSlot()
    def onCellClick(self):
        modifiers = QApplication.keyboardModifiers()
        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            if modifiers == Qt.AltModifier and \
                        currentQTableWidgetItem.text() != "":
                self.parent().resultswind.viewOnDM(currentQTableWidgetItem.text())
            
            row = self.tableWidget.row(currentQTableWidgetItem)
            col = self.tableWidget.column(currentQTableWidgetItem)
            self.deviceArchCBox.setCurrentIndex(self.archSubs[row, col])
            print(" Selected substrate #",
                  str(Acquisition().getSubstrateNumber(row,col)),
                  " Architecture: ",self.deviceArchCBox.currentText())
        
    # Logic to set and validate substrate name in table  
    def checkMatch(self, item):
        row = item.row()
        column = item.column()
        displayMultipleSamplesError = False
        displaySubNameError = False
        ItemList = QListWidget
        if self.tableWidget.item(row,column).text() !="":
            ItemList = self.tableWidget.findItems(self.tableWidget.item(row,column).text(), Qt.MatchExactly)
            subList = []
            if len(ItemList) > 1:
                for Item in ItemList:
                    subList.append(Acquisition().getSubstrateNumber(Item.row(),Item.column()))
                displayMultipleSamplesError = True
            if self.isValidSubName(self.tableWidget.item(row,column).text()) is False and \
                self.parent().config.validateSubName:
                displaySubNameError = True
                self.tableWidget.item(row,column).setText("")
            #self.checkCreateLotDM(self.tableWidget.item(row,column).text())
        self.parent().acquisitionwind.acquisitionTime()
                
        if displayMultipleSamplesError:
            msgBox = QMessageBox()
            msgBox.setIcon( QMessageBox.Information )
            msgBox.setText( "Multiple substrates with the same name already exist. Please change" )
            msgBox.setInformativeText(str(subList))
            msgBox.exec_()

        if displaySubNameError:
            print(" Naming format for substrate #",
                  str(Acquisition().getSubstrateNumber(row, column)),
                  "is not correct. Please change.")
            msgBox2 = QMessageBox()
            msgBox2.setIcon( QMessageBox.Information )
            msgBox2.setText( "Format for the substrate name is not correct, please use:" )
            msgBox2.setInformativeText("NF180323AA \
                    \nNF: user initials\n180323: date in YYMMDD format \
                    \nAA: sequential code (AA, AB, AC, ..., BK,...")
            msgBox2.exec_()

    # Validate substrate names:
    def isValidSubName(self, sub):
        try:
            if re.match("^[A-Z][A-Z]$", sub[0:2]) == None or \
                sub[2:8] != datetime.strptime(sub[2:8], "%y%m%d").strftime('%y%m%d') or \
                re.match("^[A-Z][A-Z]$", sub[8:10]) == None or \
                len(sub)!=10:
                raise ValueError
            return True
        except ValueError:
            return False

    # Enable and disable fields (flag is either True or False) during acquisition.
    def enableSamplePanel(self, flag):
        self.holderTypeCBox.setEnabled(flag)
        self.operatorText.setEnabled(flag)
        self.commentsText.setEnabled(flag)
        self.loadButton.setEnabled(flag)
        self.saveButton.setEnabled(flag)
        self.tableWidget.setEnabled(flag)
        self.tableWidget.clearSelection()
        if flag is False:
            self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        else:
            self.tableWidget.setEditTriggers(QAbstractItemView.DoubleClicked)

    # Change color in sample cells depending on the acqusition status
    def colorCellAcq(self,row,column,color):
        if color == "red":
            self.tableWidget.item(row, column).setBackground(QColor(255,0,0))
        if color == "white":
            self.tableWidget.item(row, column).setBackground(QColor(255,255,255))
        if color == "green":
            self.tableWidget.item(row, column).setBackground(QColor(0,255,0))
        if color == "yellow":
            self.tableWidget.item(row, column).setBackground(QColor(255,255,0))
        if color == "grey":
            self.tableWidget.item(row, column).setBackground(QColor(192,192,192))
        if color == "cyan":
            self.tableWidget.item(row, column).setBackground(QColor(0,255,255))

    # Reset color in sample cells
    def resetCellAcq(self):
        for i in range(self.parent().config.numSubsHolderCol):
            for j in range(self.parent().config.numSubsHolderRow):
                self.tableWidget.item(i, j).setBackground(QColor(255,255,255))
        self.disableBrokenCells(self.parent().config.brokenCells)

    # Reset color in single cell
    def resetSingleCellAcq(self, item):
        i = item.row()
        j = item.column()
        self.tableWidget.item(i, j).setBackground(QColor(255,255,255))

    # Clear names in cells
    def clearCells(self):
        for i in range(self.parent().config.numSubsHolderCol):
            for j in range(self.parent().config.numSubsHolderRow):
                self.tableWidget.setItem(i,j,QTableWidgetItem(''))
                self.tableWidget.item(i, j).setBackground(QColor(255,255,255))
        self.activeSubs = np.ones((4,4), dtype=bool)
        self.disableBrokenCells(self.parent().config.brokenCells)

    # Check if table is filled or empty
    def checkTableEmpty(self, numRow, numCol):
        for i in range(numRow):
            for j in range(numCol):
                if self.tableWidget.item(i,j).text() != "" and self.activeSubs[i,j] == True:
                    return False
        return True
    
    # Check if each cell is occupied or not by a substrate and show in table.
    def checkLoadedCells(self):
        self.clearCells()
        # Activate switchbox
        msg = "Activating switchbox and sourcemeter..."
        logger.info(msg)
        print(msg)
        try:
            self.switch_box = SwitchBox(self.parent().config.switchboxID)
            msg= " Switchbox activated."
        except:
            msg = " Switchbox not activated: no acquisition possible"
            return False

        # Activate sourcemeter
        try:
            self.source_meter = SourceMeter(self.parent().config.sourcemeterID)
            self.source_meter.set_limit(voltage=20., current=1.)
            self.source_meter.set_mode('VOLT')
            self.source_meter.on()
            msg += "\n Sourcemeter activated."
        except:
            msg += "\n Sourcemeter not activated: no acquisition possible"
            return False
        logger.info(msg)
        print(msg)
        avCurrent = 0
        for i in range(self.parent().config.numSubsHolderRow):
            for j in range(self.parent().config.numSubsHolderCol):
                for dev in range(1,7):
                    self.switch_device(i, j, dev)
                    self.source_meter.set_output(voltage = self.parent().config.voltageCheckCell)
                    time.sleep(self.parent().config.acqHoldTime)
                    current = self.source_meter.read_values(self.parent().config.deviceArea)[1]
                    avCurrent = (avCurrent*(dev-1)+current)/dev
                    print("(sub,dev): ("+str(i)+str(j)+str(dev)+") - Current: ",current," - avCurrent",avCurrent)
                print(avCurrent)
                if avCurrent>self.parent().config.currentCheckCell:
                    self.colorCellAcq(i,j,"cyan")
                else:
                    self.colorCellAcq(i,j,"white")
                QApplication.processEvents()
                    
        time.sleep(self.parent().config.acqHoldTime)
        try:
            self.switch_box.open_all()
            del self.switch_box
            self.source_meter.off()
            del self.source_meter
            msg = "Switchbox and Sourcemeter deactivated"
        except:
            msg = " Failed to deactivate Switchbox and Sourcemeter"
        
        logger.info(msg)
        print(msg)

    # Switch devices on/off
    def switch_device(self, i,j, dev_id):
        "Switch operation devices"
        sub  = int((4-j)*4-i)
        self.switch_box.connect(sub, dev_id)

    # Load device names and configuration
    def loadCsvSubstrates(self):
        import csv
        try:
            filename = QFileDialog.getOpenFileName(self,
                        "Open CSV substrates file",
                        self.parent().config.substrateFolder,"*.csv")
            with open(filename[0], 'rU') as inputFile:
                input = csv.reader(inputFile)
                devConf=[]
                for row in input:
                    devConf.append(row)
            for i in range(self.parent().config.numSubsHolderRow):
                for j in range(self.parent().config.numSubsHolderCol):
                    try:
                        self.tableWidget.setItem(i,j,QTableWidgetItem(devConf[i][j]))
                        self.disableBrokenCells(self.parent().config.brokenCells)
                    except:
                        pass
            print("Substrates configuration loaded from:",filename[0])
            logger.info("Substrates configuration loaded from:"+filename[0])
        except:
            print("Error in loading Substrates configuration")
            logger.info("Error in loading Substrates configuration")

    # Save device names and configuration
    def saveCsvSubstrates(self):
        import csv
        devConf=[['']*4 for i in range(4)]
        for i in range(self.parent().config.numSubsHolderRow):
            for j in range(self.parent().config.numSubsHolderCol):
                devConf[i][j] = self.tableWidget.item(i,j).text()
        try:
            filename = QFileDialog.getSaveFileName(self,
                    "Save CSV substrates file",
                    self.parent().config.substrateFolder,"*.csv")
            with open(filename[0], 'w', newline='') as inputFile:
                csvwrite = csv.writer(inputFile)
                for i in range(self.parent().config.numSubsHolderRow):
                    csvwrite.writerow(devConf[i])
            print("Substrate configuration saved to:",filename[0])
            logger.info("Substrate configuration saved to:"+filename[0])
        except:
            print("Error in saving substrate configuration")
            logger.info("Error in saving substrate configuration")

    # Logic to save deviceArea on config when done editing the corresponding field
    def setDeviceArea(self):
        self.parent().config.conf['Devices']['deviceArea'] = str(self.deviceAreaText.text())
        self.parent().config.saveConfig(self.parent().config.configFile)
        self.parent().config.readConfig(self.parent().config.configFile)
    
    ####################################################################
    #   DM related methods
    ####################################################################

    # View entry in DM page for substrate/device
    def viewOnDM(self, deviceID):
        print("\nOpening entry in DM for Lot:",deviceID[:8])
        db, connFlag = self.connectDM()
        if connFlag == False:
            print("Abort")
            return
        try:
            #print(db.collection_names())
            #entry = db.Measurement.find_one({'substrate':deviceID[:10]})
            entry = db.Lot.find_one({'label':deviceID[:8]})
            webbrowser.open("http://gridedgedm.mit.edu/#/lot-view/"+str(entry['_id']))
        except:
            print(" No data entry for this substrate found in DM. If appropriate, please add new one")
            webbrowser.open("http://gridedgedm.mit.edu/#/lot-view/")

    # Remove Entry from DM - disabled by default
    def removeEntryDM(self, deviceID):
        print("\nOpening entry in DM for Lot:",deviceID[:8])
        db, connFlag = self.connectDM()
        if connFlag == False:
            print("Abort")
            return
        try:
            #print(db.collection_names())
            #db.Lot.delete_one({'_id': '59973a1b70be99396fb85357'})
            #db.Lot.delete_one({'owner': 'MH'})
            db.Lot.delete_one({'label':deviceID[:8]})
            for cursor in db.Measurement.find({'substrate':deviceID}):
                db.Measurement.delete_one({'substrate': deviceID})
            print(" Entry for substrate", deviceID,"deleted")
        except:
            print(" Error in deleting entry for substrate", deviceID[:8],". Aborting")

    # Show Json info on a substrate in Database - disabled by default
    def showJsonInfoDM(self, deviceID):
        print("\nOpening entry in DM for Lot:",deviceID[:8])
        db, connFlag = self.connectDM()
        if connFlag == False:
            print("Abort")
            return
        try:
            #print(db.collection_names())
            #print("\nMeasurements\n")
            #print("Number of Measurement entries: ",db.Measurement.find().count())
            for cursor in db.Measurement.find({'substrate':deviceID}):
                print(cursor,"\n")
            #print("\nLots\n")
            #print("Number of Lot entries: ",db.Lot.find().count())
            #for cursor in db.Lot.find():
            #    print(cursor)
            print(db.Lot.find_one({'label':deviceID[:8]}))
        except:
            print(" Error!")

    # Show Json info on a substrate in Database - disabled by default
    def saveJsonInfoDM(self, deviceID):
        print("\nOpening entry in DM for Lot:",deviceID[:8])
        db, connFlag = self.connectDM()
        if connFlag == False:
            print("Abort")
            return
        try:
            entry = db.Lot.find_one({'label':deviceID[:8]})
            entry.pop('_id',None)
            fname = deviceID[:8]+"_"+str(datetime.now().strftime('%Y%m%d-%H%M%S-%f'))+".json"
            with open(self.parent().config.substrateFolder+fname,'w') as outfile:
                json.dump(entry,outfile)
            msg = " Created json file: "+self.parent().config.substrateFolder+fname
            print(msg)
            logger.info(msg)
        except:
            print(" Error!")

    def addTagDM(self, deviceID, row, col):
        print("\nOpening entry in DM for Lot:",deviceID[:8])
        db, connFlag = self.connectDM()
        if connFlag == False:
            print("Abort")
            return
        try:
            # To add tags to Measurement collection
            for cursor in db.Measurement.find({'substrate':deviceID, 'itemId' : str(1), 'name': 'JV_r'}):
                print(cursor,"\n")
            for i in range(1,7):
                db.Measurement.update({'substrate':deviceID, 'itemId' : str(i), 'name': 'JV_r'},{"$set" : {'DevArchitecture':['0_blank']}},False,True)
                db.Measurement.update({'substrate':deviceID, 'itemId' : str(i), 'name': 'JV_f'},{"$set" : {'DevArchitecture':['0_blank']}},False,True)
                db.Measurement.update({'substrate':deviceID, 'itemId' : str(i), 'name': 'JV_dark_f'},{"$set" : {'DevArchitecture':['0_blank']}},False,True)
                db.Measurement.update({'substrate':deviceID, 'itemId' : str(i), 'name': 'JV_dark_r'},{"$set" : {'DevArchitecture':['0_blank']}},False,True)
                db.Measurement.update({'substrate':deviceID, 'itemId' : str(i), 'name': 'tracking'},{"$set" : {'DevArchitecture':['0_blank']}},False,True)
            '''
            # To add tags to Lot collection
            for cursor in db.Lot.find({'label':deviceID[:8]}):
                #print(cursor,"\n")
                print(db.Lot.find_one({'_id': cursor['_id'], 'substrates.label':deviceID}),"\n")
                db.Lot.update_one({'_id': cursor['_id'], 'substrates.label':deviceID},{"$set" : {'substrates.$.architecture':'0_blank'}},False,True)
                #db.Lot.update_one({'_id': cursor['_id'], 'substrates.label':deviceID},{"$set" : {'substrates.$.material':'GREAT'}},False,True)
                #db.Lot.update_one({'_id': cursor['_id'], 'substrates.label':deviceID},{"$set" : {'substrates.$.isCollapsed':True}},False,True)
                print(db.Lot.find_one({'_id': cursor['_id'], 'substrates.label':deviceID}),"\n")
            '''
        except:
            pass

    # View entry in DM page for substrate/device
    def checkCreateLotDM(self, deviceID, row, col):
        print("\nOpening entry in DM for Lot:",deviceID[:8])
        db, connFlag = self.connectDM()
        if connFlag == False:
            print("Abort")
            return
        try:
            entry = db.Lot.find_one({'label':deviceID[:8]})
            if entry:
                db.Lot.update_one({ '_id': entry['_id'] },{"$push": self.getArchConfig(deviceID, row, col)}, upsert=False)
                msg = " Data entry for this batch found in DM. Created substrate: "+deviceID
            else:
                print(" No data entry for this substrate found in DM. Creating new one...")
                jsonData = {'label' : deviceID[:8], 'date' : deviceID[2:8], 'description': '', 'notes': '', 'tags': [], 'substrates': []}
                db_entry = db.Lot.insert_one(json.loads(json.dumps(jsonData)))
                db.Lot.update_one({ '_id': db_entry.inserted_id },{"$push": self.getArchConfig(deviceID,row,col)}, upsert=False)
                msg = " Created batch: " + deviceID[:8] + " and device: "+deviceID +"  with Architecture: "+\
                self.deviceArchCBox.itemText(self.archSubs[row,col])
            print(msg)
            logger.info(msg)
        except:
            print(" Connection with DM via Mongo cannot be established.")

    # Get architecture configuration files.
    def getArchConfig(self, deviceID, row, col):
        try:
            #f = self.deviceArchCBox.currentText()+".json"
            f = self.deviceArchCBox.itemText(self.archSubs[row,col])+".json"
            with open(self.parent().config.archFolder+f, encoding='utf-8') as data_file:
                data = json.loads(data_file.read())
            data['substrates']['label'] = deviceID
        except:
            data = {}
        return data

    # Connect to DM
    def connectDM(self):
        self.dbConnectInfo = self.parent().dbconnectionwind.getDbConnectionInfo()
        try:
            conn = DataManagement(self.dbConnectInfo)
            client, _ = conn.connectDB()
            db = client[self.dbConnectInfo[2]]
            #print(" Connected to DM")
            return db, True
        except:
            print(" Connection to DM failed")
            return None, False

    # Define preset architectures if missing
    def archSubstrate(self, ind):
        if ind == 0:
            name = "0_blank"
            return name, {'substrates': {'isCollapsed': False, 'label': 'deviceID', 'architecture' : '0_blank', 'material': '', 'flex': False, 'area': '', 'layers': [], 'attachments': [], 'devices': [{'size': '', 'measurements': []}, {'size': '', 'measurements': []}, {'size': '', 'measurements': []}, {'size': '', 'measurements': []}, {'size': '', 'measurements': []}, {'size': '', 'measurements': []}]}}
        if ind == 1:
            name = "FTO-SnO2-Perovsk-Spiro-Au"
            return name, {'substrates': {'isCollapsed': False, 'label': 'DD190211AA', 'architecture' : 'FTO-SnO2-Perovsk-Spiro-Au', 'material': 'FTO', 'flex': False, 'area': '', 'layers': [{'name': 'SnO2', 'description': '', 'material': '', 'thickness': '', 'deposition': '', 'deponotes': '', 'measurements': [], 'status': {'open': False}, 'depositiontool': 'Spincoated'}, {'name': 'Perovskite (Triple Cation)', 'description': '', 'material': '', 'thickness': '', 'deposition': '', 'deponotes': '', 'measurements': [], 'status': {'open': False}, 'depositiontool': 'Spincoated'}, {'name': 'Spiro-OMeTAD', 'description': '', 'material': '', 'thickness': '', 'deposition': '', 'deponotes': '', 'measurements': [], 'status': {'open': False}, 'depositiontool': 'Spincoated'}, {'name': 'Au', 'description': '', 'material': '', 'thickness': '', 'deposition': '', 'deponotes': '', 'measurements': [], 'status': {'open': True}, 'depositiontool': 'Thermally Evaporated'}], 'attachments': [], 'devices': [{'number': '1', 'size': '0.06 cm2', 'measurements': []}, {'number': '1', 'size': '0.06 cm2', 'measurements': []}, {'size': '', 'measurements': []}, {'size': '', 'measurements': []}, {'size': '', 'measurements': []}, {'size': '', 'measurements': []}]}}
        if ind == 2:
            name = "FTO-SnO2-Perovsk-Spiro-MoOx-Al"
            return name, {'substrates': {'isCollapsed': False, 'label': 'DD190211AB', 'architecture' : 'FTO-SnO2-Perovsk-Spiro-MoOx-Al', 'material': 'FTO', 'flex': False, 'area': '', 'layers': [{'name': 'SnO2', 'description': '', 'material': '', 'thickness': '', 'deposition': '', 'deponotes': '', 'measurements': [], 'status': {'open': False}, 'depositiontool': 'Spincoated'}, {'name': 'Perovskite (Triple Cation)', 'description': '', 'material': '', 'thickness': '', 'deposition': '', 'deponotes': '', 'measurements': [], 'status': {'open': False}, 'depositiontool': 'Spincoated'}, {'name': 'Spiro-OMeTAD', 'description': '', 'material': '', 'thickness': '', 'deposition': '', 'deponotes': '', 'measurements': [], 'status': {'open': False}, 'depositiontool': 'Spincoated'}, {'name': 'MoOx/Al', 'description': '', 'material': '', 'thickness': '', 'deposition': '', 'deponotes': '', 'measurements': [], 'status': {'open': False}, 'depositiontool': 'Thermally Evaporated'}], 'attachments': [], 'devices': [{'number': '1', 'size': '0.06 cm2', 'measurements': []}, {'number': '1', 'size': '0.06 cm2', 'measurements': []}, {'size': '', 'measurements': []}, {'size': '', 'measurements': []}, {'size': '', 'measurements': []}, {'size': '', 'measurements': []}]}}
        if ind == 3:
            name = "FTO-PEDOTPSS-Perovskite-PCBM-BCP-Ag"
            return name, {'substrates': {'isCollapsed': False, 'label': 'DD190211AC', 'architecture' : 'FTO-PEDOTPSS-Perovskite-PCBM-BCP-Ag', 'material': 'FTO', 'flex': False, 'area': '', 'layers': [{'name': 'PEDOT:PSS', 'description': '', 'material': '', 'thickness': '', 'deposition': '', 'deponotes': '', 'measurements': [], 'status': {'open': False}, 'depositiontool': 'Spincoated'}, {'name': 'Perovskite', 'description': '', 'material': '', 'thickness': '', 'deposition': '', 'deponotes': '', 'measurements': [], 'status': {'open': False}, 'depositiontool': 'Spincoated'}, {'name': 'PCBM', 'description': '', 'material': '', 'thickness': '', 'deposition': '', 'deponotes': '', 'measurements': [], 'status': {'open': False}, 'depositiontool': 'Spincoated'}, {'name': 'BCP', 'description': '', 'material': '', 'thickness': '', 'deposition': '', 'deponotes': '', 'measurements': [], 'status': {'open': False}}, {'name': 'Ag', 'description': '', 'material': '', 'thickness': '', 'deposition': '', 'deponotes': '', 'measurements': [], 'status': {'open': False}, 'depositiontool': 'Thermally Evaporated'}], 'attachments': [], 'devices': [{'number': '1', 'size': '0.06 cm2', 'measurements': []}, {'number': '1', 'size': '0.06 cm2', 'measurements': []}, {'size': '', 'measurements': []}, {'size': '', 'measurements': []}, {'size': '', 'measurements': []}, {'size': '', 'measurements': []}]}}
        if ind == 4:
            name = "ITO-SnO2-Perovsk-Spiro-Au"
            return name, {'substrates': {'isCollapsed': False, 'label': 'DD190211AA', 'architecture' : 'ITO-SnO2-Perovsk-Spiro-Au', 'material': 'ITO', 'flex': False, 'area': '', 'layers': [{'name': 'SnO2', 'description': '', 'material': '', 'thickness': '', 'deposition': '', 'deponotes': '', 'measurements': [], 'status': {'open': False}, 'depositiontool': 'Spincoated'}, {'name': 'Perovskite (Triple Cation)', 'description': '', 'material': '', 'thickness': '', 'deposition': '', 'deponotes': '', 'measurements': [], 'status': {'open': False}, 'depositiontool': 'Spincoated'}, {'name': 'Spiro-OMeTAD', 'description': '', 'material': '', 'thickness': '', 'deposition': '', 'deponotes': '', 'measurements': [], 'status': {'open': False}, 'depositiontool': 'Spincoated'}, {'name': 'Au', 'description': '', 'material': '', 'thickness': '', 'deposition': '', 'deponotes': '', 'measurements': [], 'status': {'open': True}, 'depositiontool': 'Thermally Evaporated'}], 'attachments': [], 'devices': [{'number': '1', 'size': '0.06 cm2', 'measurements': []}, {'number': '1', 'size': '0.06 cm2', 'measurements': []}, {'size': '', 'measurements': []}, {'size': '', 'measurements': []}, {'size': '', 'measurements': []}, {'size': '', 'measurements': []}]}}
        if ind == 5:
            name = "ITO-SnO2-Perovsk-Spiro-MoOx-Al"
            return name, {'substrates': {'isCollapsed': False, 'label': 'DD190211AB', 'architecture' : 'ITO-SnO2-Perovsk-Spiro-MoOx-Al', 'material': 'ITO', 'flex': False, 'area': '', 'layers': [{'name': 'SnO2', 'description': '', 'material': '', 'thickness': '', 'deposition': '', 'deponotes': '', 'measurements': [], 'status': {'open': False}, 'depositiontool': 'Spincoated'}, {'name': 'Perovskite (Triple Cation)', 'description': '', 'material': '', 'thickness': '', 'deposition': '', 'deponotes': '', 'measurements': [], 'status': {'open': False}, 'depositiontool': 'Spincoated'}, {'name': 'Spiro-OMeTAD', 'description': '', 'material': '', 'thickness': '', 'deposition': '', 'deponotes': '', 'measurements': [], 'status': {'open': False}, 'depositiontool': 'Spincoated'}, {'name': 'MoOx/Al', 'description': '', 'material': '', 'thickness': '', 'deposition': '', 'deponotes': '', 'measurements': [], 'status': {'open': False}, 'depositiontool': 'Thermally Evaporated'}], 'attachments': [], 'devices': [{'number': '1', 'size': '0.06 cm2', 'measurements': []}, {'number': '1', 'size': '0.06 cm2', 'measurements': []}, {'size': '', 'measurements': []}, {'size': '', 'measurements': []}, {'size': '', 'measurements': []}, {'size': '', 'measurements': []}]}}
        if ind == 6:
            name = "ITO-PEDOTPSS-Perovskite-PCBM-BCP-Ag"
            return name, {'substrates': {'isCollapsed': False, 'label': 'DD190211AC', 'architecture': 'ITO-PEDOTPSS-Perovskite-PCBM-BCP-Ag', 'material': 'ITO', 'flex': False, 'area': '', 'layers': [{'name': 'PEDOT:PSS', 'description': '', 'material': '', 'thickness': '', 'deposition': '', 'deponotes': '', 'measurements': [], 'status': {'open': False}, 'depositiontool': 'Spincoated'}, {'name': 'Perovskite', 'description': '', 'material': '', 'thickness': '', 'deposition': '', 'deponotes': '', 'measurements': [], 'status': {'open': False}, 'depositiontool': 'Spincoated'}, {'name': 'PCBM', 'description': '', 'material': '', 'thickness': '', 'deposition': '', 'deponotes': '', 'measurements': [], 'status': {'open': False}, 'depositiontool': 'Spincoated'}, {'name': 'BCP', 'description': '', 'material': '', 'thickness': '', 'deposition': '', 'deponotes': '', 'measurements': [], 'status': {'open': False}}, {'name': 'Ag', 'description': '', 'material': '', 'thickness': '', 'deposition': '', 'deponotes': '', 'measurements': [], 'status': {'open': False}, 'depositiontool': 'Thermally Evaporated'}], 'attachments': [], 'devices': [{'number': '1', 'size': '0.06 cm2', 'measurements': []}, {'number': '1', 'size': '0.06 cm2', 'measurements': []}, {'size': '', 'measurements': []}, {'size': '', 'measurements': []}, {'size': '', 'measurements': []}, {'size': '', 'measurements': []}]}}
