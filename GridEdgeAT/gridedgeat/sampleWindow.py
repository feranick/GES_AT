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

import sys, re, os.path
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

####################################################################
#   Sample Window
####################################################################
class SampleWindow(QMainWindow):
    def __init__(self, parent=None):
        super(SampleWindow, self).__init__(parent)
        self.activeSubs = np.ones((self.parent().config.numSubsHolderRow,
                self.parent().config.numSubsHolderCol),
                dtype=bool)
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
        self.populateArchCBox()

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
        
        # This allows for background coloring of a cell
        for i in range(self.parent().config.numSubsHolderCol):
            for j in range(self.parent().config.numSubsHolderRow):
                self.tableWidget.setItem(i,j,QTableWidgetItem())
                self.tableWidget.item(i,j).setToolTip("Substrate #"+\
                    str(Acquisition().getSubstrateNumber(i,j)))
    
        self.disableBrokenCells(self.parent().config.brokenCells)
        
        self.checkCellsButton = QPushButton(self.centralwidget)
        self.checkCellsButton.setGeometry(QRect(10, 460, 80, 80))
        self.checkCellsButton.setObjectName("checkSample")
        #self.checkCellsButton.clicked.connect(self.loadCsvSubstrates)
        self.checkCellsButton.setEnabled(False)
        
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
            with open(self.parent().config.archFolder+'blank.json','w') as outfile:
                json.dump(self.blankSubstrate(),outfile)

        for ind, f in enumerate(sorted(os.listdir(self.parent().config.archFolder))):
            if (os.path.splitext(f)[-1] == ".json"):
                self.deviceArchCBox.addItem(os.path.splitext(f)[0])
    
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
                self.menu.addAction(selectCellAction)
                self.menu.addAction(viewDMEntryAction)
                self.menu.addSeparator()
                #self.menu.addAction(showJsonInfoDMAction)
                self.menu.addAction(saveJsonInfoDMAction)
                #self.menu.addAction(removeEntryDMAction)
                #self.menu.addAction(checkCreateLotDMAction)
                self.menu.popup(QCursor.pos())
                selectCellAction.triggered.connect(lambda: self.selectCell(row,col))
                viewDMEntryAction.triggered.connect(lambda: self.viewOnDM(self.tableWidget.item(row,col).text()))
                showJsonInfoDMAction.triggered.connect(lambda: self.showJsonInfoDM(self.tableWidget.item(row,col).text()))
                saveJsonInfoDMAction.triggered.connect(lambda: self.saveJsonInfoDM(self.tableWidget.item(row,col).text()))
                removeEntryDMAction.triggered.connect(lambda: self.removeEntryDM(self.tableWidget.item(row,col).text()))
                checkCreateLotDMAction.triggered.connect(lambda: self.checkCreateLotDM(self.tableWidget.item(row,col).text()))
        except:
            pass

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
            print(" Selected substrate #",
                str(Acquisition().getSubstrateNumber(self.tableWidget.row(currentQTableWidgetItem),
                  self.tableWidget.column(currentQTableWidgetItem))))
        
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
    #   Sample Window
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
            db.Lot.delete_one({'label':deviceID[:8]})
            #db.Lot.delete_one({'_id': '59973a1b70be99396fb85357'})
            #db.Lot.delete_one({'owner': 'MH'})
            #for cursor in db.Measurement.find():
            #    db.Measurement.delete_one({'substrate': deviceID})
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
            #for cursor in db.Measurement.find():
            #    print(cursor)
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

    # View entry in DM page for substrate/device
    def checkCreateLotDM(self, deviceID):
        print("\nOpening entry in DM for Lot:",deviceID[:8])
        db, connFlag = self.connectDM()
        if connFlag == False:
            print("Abort")
            return
        try:
            entry = db.Lot.find_one({'label':deviceID[:8]})
            if entry:
                db.Lot.update_one({ '_id': entry['_id'] },{"$push": self.getArchConfig(deviceID)}, upsert=False)
                msg = " Data entry for this batch found in DM. Created substrate: "+deviceID
            else:
                print(" No data entry for this substrate found in DM. Creating new one...")
                jsonData = {'label' : deviceID[:8], 'date' : deviceID[2:8], 'description': '', 'notes': '', 'tags': [], 'substrates': []}
                db_entry = db.Lot.insert_one(json.loads(json.dumps(jsonData)))
                db.Lot.update_one({ '_id': db_entry.inserted_id },{"$push": self.getArchConfig(deviceID)}, upsert=False)
                msg = " Created batch: " + deviceID[:8] + " and device: "+deviceID
            print(msg)
            logger.info(msg)
        except:
            print(" Connection with DM via Mongo cannot be established.")

    # Get architecture configuration files.
    def getArchConfig(self, deviceID):
        try:
            f = self.deviceArchCBox.currentText()+".json"
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

    def blankSubstrate(self):
        return {'substrates': {'isCollapsed': False, 'label': 'deviceID', 'material': '', 'flex': False, 'area': '', 'layers': [], 'attachments': [], 'devices': [{'size': '', 'measurements': []}, {'size': '', 'measurements': []}, {'size': '', 'measurements': []}, {'size': '', 'measurements': []}, {'size': '', 'measurements': []}, {'size': '', 'measurements': []}]}}

