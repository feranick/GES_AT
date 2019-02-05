'''
ResultsWindow.py
-------------
Classes for providing a graphical user interface
for the resultsWindow

Copyright (C) 2017-2019 Nicola Ferralis <ferralis@mit.edu>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

'''
import sys, random, math, json, requests, webbrowser
import numpy as np
import pandas as pd
from datetime import datetime
from PyQt5.QtWidgets import (QMainWindow,QPushButton,QVBoxLayout,QFileDialog,QWidget,
                             QGridLayout,QGraphicsView,QLabel,QComboBox,QLineEdit,
                             QMenuBar,QStatusBar, QApplication,QTableWidget,
                             QTableWidgetItem,QAction,QHeaderView,QMenu,QHBoxLayout,
                             QAbstractItemView)
from PyQt5.QtCore import (QRect,pyqtSlot,pyqtSignal,Qt)
from PyQt5.QtGui import (QColor,QCursor)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

from .dataManagement import *
from . import logger

####################################################################
#   Results Window
####################################################################
class ResultsWindow(QMainWindow):
    def __init__(self, parent=None):
        super(ResultsWindow, self).__init__(parent)
        self.deviceID = np.zeros((0,1))
        self.perfData = np.zeros((0,9))
        self.JV = np.array([])
        self.setupDataFrame()
        self.csvFolder = self.parent().config.csvSavingFolder
        self.initUI()
        self.initPlots(self.perfData)
        self.initJVPlot()
        self.show()
    
    # Define UI elements
    def initUI(self):
        self.setGeometry(380, 30, 1180, 950)
        self.setWindowTitle('Results Panel')
        self.setFixedSize(self.size())
        
        # A figure instance to plot on
        self.figureMPP = plt.figure()
        self.figureJVresp = plt.figure()
        self.figurePVresp = plt.figure()
        self.figureJVresp.subplots_adjust(left=0.15, right=0.95, top=0.95, bottom=0.15)
        self.figurePVresp.subplots_adjust(left=0.15, right=0.95, top=0.95, bottom=0.15)
        self.figureMPP.subplots_adjust(left=0.08, right=0.98, top=0.95, bottom=0.20)
        
        self.centralwidget = QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        
        self.jvGridLayoutWidget = QWidget(self.centralwidget)
        self.jvGridLayoutWidget.setGeometry(QRect(0, 30, 1180, 455))
        self.mppGridLayoutWidget = QWidget(self.centralwidget)
        self.mppGridLayoutWidget.setGeometry(QRect(0, 475, 1180, 290))

        self.VLayout = QVBoxLayout(self.jvGridLayoutWidget)
        self.jvHLayout = QHBoxLayout()
        
        self.canvasJVresp = FigureCanvas(self.figureJVresp)
        self.toolbarJVresp = CustomToolbar(self.canvasJVresp, self.figureJVresp, self)
        self.toolbarJVresp.setMaximumHeight(30)
        self.toolbarJVresp.setStyleSheet("QToolBar { border: 0px }")

        self.canvasPVresp = FigureCanvas(self.figurePVresp)
        self.toolbarPVresp = CustomToolbar(self.canvasPVresp, self.figurePVresp, self)
        self.toolbarPVresp.setMaximumHeight(30)
        self.toolbarPVresp.setStyleSheet("QToolBar { border: 0px }")

        self.jvLayout = QVBoxLayout()
        self.pvLayout = QVBoxLayout()

        self.jvLayout.addWidget(self.toolbarJVresp)
        self.jvLayout.addWidget(self.canvasJVresp)
        self.jvHLayout.addLayout(self.jvLayout)
        
        self.pvLayout.addWidget(self.toolbarPVresp)
        self.pvLayout.addWidget(self.canvasPVresp)
        self.jvHLayout.addLayout(self.pvLayout)
        self.VLayout.addLayout(self.jvHLayout)

        self.mppLayout = QVBoxLayout(self.mppGridLayoutWidget)

        self.canvasMPP = FigureCanvas(self.figureMPP)
        self.toolbarMPP = NavigationToolbar(self.canvasMPP, self)
        self.toolbarMPP.setMaximumHeight(30)
        self.toolbarMPP.setStyleSheet("QToolBar { border: 0px }")

        self.mppLayout.addWidget(self.toolbarMPP)
        self.mppLayout.addWidget(self.canvasMPP)

        self.resTableW = 1160
        self.resTableH = 145
        self.resTableWidget = QTableWidget(self.centralwidget)
        self.resTableWidget.setGeometry(QRect(10, 770, self.resTableW, self.resTableH))
        self.resTableWidget.setColumnCount(11)
        self.resTableWidget.setRowCount(0)
        self.resTableWidget.setItem(0,0, QTableWidgetItem(""))
        self.resTableWidget.setHorizontalHeaderItem(0,QTableWidgetItem("Device ID"))
        self.resTableWidget.setHorizontalHeaderItem(1,QTableWidgetItem("Av Voc [V]"))
        self.resTableWidget.setHorizontalHeaderItem(2,QTableWidgetItem(u"Av Jsc [mA/cm\u00B2]"))
        self.resTableWidget.setHorizontalHeaderItem(3,QTableWidgetItem("Av VPP [V]"))
        self.resTableWidget.setHorizontalHeaderItem(4,QTableWidgetItem("Av MPP [mW/cm\u00B2]"))
        self.resTableWidget.setHorizontalHeaderItem(5,QTableWidgetItem("Av FF"))
        self.resTableWidget.setHorizontalHeaderItem(6,QTableWidgetItem("Av PCE [%]"))
        self.resTableWidget.setHorizontalHeaderItem(7,QTableWidgetItem("Illumination"))
        self.resTableWidget.setHorizontalHeaderItem(8,QTableWidgetItem("Tracking time [s]"))
        self.resTableWidget.setHorizontalHeaderItem(9,QTableWidgetItem("Acq Date"))
        self.resTableWidget.setHorizontalHeaderItem(10,QTableWidgetItem("Acq Time"))
        self.resTableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.resTableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.resTableWidget.itemClicked.connect(self.onCellClick)
        self.setCentralWidget(self.centralwidget)

        # Make Menu for plot related calls
        self.menuBar = QMenuBar(self)
        self.menuBar.setGeometry(0,0,1150,25)

        self.loadMenu = QAction("&Load Local Data", self)
        self.loadMenu.setShortcut("Ctrl+o")
        self.loadMenu.setStatusTip('Load csv data from saved file')
        self.loadMenu.triggered.connect(self.load_csv)
        self.loadDMMenu = QAction("&Load Data from Data Management", self)
        self.loadDMMenu.setShortcut("Ctrl+Shift+o")
        self.loadDMMenu.setStatusTip('Load data from Data Management')
        self.loadDMMenu.triggered.connect(self.openWindowDM)
        self.directoryMenu = QAction("&Set directory for saved files", self)
        self.directoryMenu.setShortcut("Ctrl+d")
        self.directoryMenu.setStatusTip('Set directory for saved files')
        self.directoryMenu.triggered.connect(self.set_dir_saved)
        
        self.clearMenu = QAction("&Clear Plots", self)
        self.clearMenu.setShortcut("Ctrl+x")
        self.clearMenu.setStatusTip('Clear plots')
        self.clearMenu.triggered.connect(lambda: self.clearPlots(True))
        
        fileMenu = self.menuBar.addMenu('&File')
        fileMenu.addAction(self.loadMenu)
        fileMenu.addAction(self.loadDMMenu)
        fileMenu.addSeparator()
        fileMenu.addAction(self.directoryMenu)
        plotMenu = self.menuBar.addMenu('&Plot')
        plotMenu.addAction(self.clearMenu)
        
        self.parent().viewWindowMenus(self.menuBar, self.parent())
        
        self.statusbar = QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

    # Set directory for saved data
    def set_dir_saved(self):
        self.csvFolder = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.parent().config.conf['System']['csvSavingFolder'] = str(self.csvFolder)
        self.parent().config.saveConfig(self.parent().config.configFile)
        self.parent().config.readConfig(self.parent().config.configFile)
        msg = "CSV Files will be saved in: "+self.csvFolder
        print(msg)
        logger.info(msg)
    
    # Define axis parametrs for plots
    def plotSettings(self, ax):
        ax.tick_params(axis='both', which='major', labelsize=8)
        ax.tick_params(axis='both', which='minor', labelsize=8)
    
    # Initialize Time-based plots
    def initPlots(self, data):
        self.figureMPP.clf()
        self.axMPP = self.figureMPP.add_subplot(111)
        self.plotSettings(self.axMPP)
        self.axMPP.set_xlabel('Time [s]',fontsize=8)
        self.axMPP.set_ylabel('Max power point \n[mW/cm$^2$]',fontsize=8)
        self.axMPP.set_autoscale_on(True)
        self.axMPP.autoscale_view(True,True,True)
        self.canvasMPP.draw()
        self.lineMPP, = self.axMPP.plot(data[:,0],data[:,4], '.-',linewidth=0.5)
    
    # Initialize JV and PV plots
    def initJVPlot(self):
        self.figureJVresp.clf()
        self.figurePVresp.clf()
        self.axJVresp = self.figureJVresp.add_subplot(111)
        self.plotSettings(self.axJVresp)
        self.axJVresp.set_xlabel('Voltage [V]',fontsize=8)
        self.axJVresp.set_ylabel('Current density [mA/cm$^2$]',fontsize=8)
        self.axJVresp.axvline(x=0, linewidth=0.5)
        self.axJVresp.axhline(y=0, linewidth=0.5)
        
        self.axPVresp = self.figurePVresp.add_subplot(111)
        self.plotSettings(self.axPVresp)
        self.axPVresp.set_xlabel('Voltage [V]',fontsize=8)
        self.axPVresp.set_ylabel('Power density [mW/cm$^2$]',fontsize=8)
        self.axPVresp.axvline(x=0, linewidth=0.5)
        self.axPVresp.axhline(y=0, linewidth=0.5)
        self.canvasJVresp.draw()
        self.canvasPVresp.draw()

    # Plot MPP with tracking
    def plotMPP(self, data):
        self.toolbarMPP.update()
        self.lineMPP.set_data(data[:,2].astype(float), abs(data[:,6].astype(float)))
        self.axMPP.relim()
        self.axMPP.autoscale_view(True,True,True)
        self.canvasMPP.draw()
    
    # Plot JV response
    def plotJVresp(self, JV):
        self.initJVPlot()
        self.toolbarJVresp.update()
        self.toolbarPVresp.update()
        self.axJVresp.plot(JV[:,0],JV[:,1], '.-',linewidth=0.5, label='Forw')
        self.axJVresp.plot(JV[:,2],JV[:,3], '.-',linewidth=0.5, label='Back')
        self.axPVresp.plot(JV[:,0],JV[:,0]*JV[:,1], '.-',linewidth=0.5, label='Forw')
        self.axPVresp.plot(JV[:,2],JV[:,2]*JV[:,3], '.-',linewidth=0.5, label='Back')
        self.axJVresp.legend(loc='lower left')
        self.axPVresp.legend(loc='upper left')
        if self.parent().config.logPlotJV:
            self.axJVresp.set_yscale('log')
            self.axPVresp.set_yscale('log')
        self.figureJVresp.tight_layout()
        self.figurePVresp.tight_layout()
        self.canvasJVresp.draw()
        self.canvasPVresp.draw()
    
    # Clear all plots and fields
    def clearPlots(self, includeTable):
        self.setWindowTitle('Results Panel')
        self.deviceID = np.zeros((0,1))
        self.perfData = np.zeros((0,8))
        self.JV = np.array([])
        self.initPlots(self.perfData)
        self.initJVPlot()
        if includeTable is True:
            self.resTableWidget.setRowCount(0)
        QApplication.processEvents()
    
    # Action upon selecting a row in the table.
    @pyqtSlot()
    def onCellClick(self):
        row = self.resTableWidget.selectedItems()[0].row()
        for j in range(self.resTableWidget.columnCount()):
            for i in range(self.resTableWidget.rowCount()):
                self.resTableWidget.item(i,j).setBackground(QColor(255,255,255))
        for j in range(self.resTableWidget.columnCount()):
            self.resTableWidget.item(row,j).setBackground(QColor(0,255,0))
        try:
            self.setWindowTitle('Results Panel - Device: '+ str(self.dfTotDeviceID.iat[0,self.resTableWidget.rowCount()-1-row][0][0]))
            self.plotData(self.dfTotDeviceID.iat[0,self.resTableWidget.rowCount()-1-row],
                self.dfTotPerfData.iat[0,self.resTableWidget.rowCount()-1-row],
                self.dfTotJV.iat[0,self.resTableWidget.rowCount()-1-row])
        except:
            pass

    # Process Key Events
    def keyPressEvent(self, event):
        if self.resTableWidget.rowCount() > 0:
            if event.key() == Qt.Key_Delete:
                selectedRows = list(set([ i.row() for i in self.resTableWidget.selectedItems()]))
                for row in selectedRows[::-1]:
                    self.selectDeviceRemove(row)

    # Enable right click on substrates for saving locally and delete
    def contextMenuEvent(self, event):
        self.menu = QMenu(self)
        rPos = self.resTableWidget.mapFromGlobal(QCursor.pos())
        if rPos.x()>0 and rPos.x()<self.resTableW and \
                rPos.y()>0 and rPos.y()<self.resTableH and \
                self.resTableWidget.rowCount() > 0 :
        
            selectCellLoadAction = QAction("&Load from csv...", self)
            selectCellLoadAction.setShortcut("Ctrl+o")
            selectCellLoadAction.setStatusTip('Load csv data from saved file')
            selectCellSaveAction = QAction('Save locally', self)
            selectCellSaveAction.setShortcut("Ctrl+s")
            viewDMEntryAction = QAction("&View Entry in Database", self)
            viewDMEntryAction.setShortcut("Ctrl+v")
            selectCellRemoveAction = QAction('Remove...', self)
            selectCellRemoveAction.setShortcut("Del")
            selectRemoveAllAction = QAction('Remove All...', self)
            selectRemoveAllAction.setShortcut("Shift+Del")
            self.menu.addAction(selectCellRemoveAction)
            self.menu.addAction(selectRemoveAllAction)
            self.menu.addSeparator()
            self.menu.addAction(selectCellLoadAction)
            self.menu.addAction(selectCellSaveAction)
            self.menu.addSeparator()
            self.menu.addAction(viewDMEntryAction)
            self.menu.popup(QCursor.pos())
            QApplication.processEvents()
            
            selectCellLoadAction.triggered.connect(self.load_csv)
            selectedRows = list(set([ i.row() for i in self.resTableWidget.selectedItems()]))
            for row in selectedRows[::-1]:
                print(self.dfTotDeviceID)
                selectCellSaveAction.triggered.connect(lambda: self.selectDeviceSaveLocally(row))
                selectCellRemoveAction.triggered.connect(lambda: self.selectDeviceRemove(row))
                selectRemoveAllAction.triggered.connect(lambda: self.clearPlots(True))
                viewDMEntryAction.triggered.connect(lambda: self.parent().samplewind.viewOnDM(self.resTableWidget.selectedItems()[0].text()))

    # Logic to save locally devices selected from results table
    def selectDeviceSaveLocally(self, row):
        try:
            #print(self.dfTotDeviceID.iat[0,row][0][0])
            #self.save_csv(self.dfTotDeviceID.iat[0,row][0][0],
            self.save_csv(self.resTableWidget.selectedItems()[0].text(),
                self.dfTotAcqParams.iloc[[row]],
                self.dfTotPerfData.iat[0,row],
                self.dfTotJV.iat[0,row])
        except:
            print("Error: cannot be saved")
    
    # Logic to remove data from devices selected from results table
    def selectDeviceRemove(self, row):
        self.dfTotDeviceID.drop(self.dfTotDeviceID.columns[row], axis=1)
        self.dfTotPerfData.drop(self.dfTotPerfData.columns[row], axis=1)
        self.dfTotJV.drop(self.dfTotJV.columns[row], axis=1)
        for l in self.axJVresp.get_lines():
            l.remove()
        for l in self.axPVresp.get_lines():
            l.remove()
        print("Removed acquisition from table: ",str(self.dfTotDeviceID.iat[0,row]))
        self.canvasJVresp.draw()
        self.canvasPVresp.draw()
        self.resTableWidget.removeRow(row)

    # Add row and initialize it within the table
    def setupResultTable(self):
        self.resTableWidget.insertRow(0)
        self.lastRowInd = 0

        ### Uncomment this to display latest acquisition last 
        #self.resTableWidget.insertRow(self.resTableWidget.rowCount())
        #self.resTableWidget.setItem(self.resTableWidget.rowCount()-1,0,
        #                                QTableWidgetItem())
        #for j in range(self.resTableWidget.columnCount()):
        #    self.resTableWidget.setItem(self.resTableWidget.rowCount(),j,
        #                                QTableWidgetItem())
        #self.lastRowInd = self.resTableWidget.rowCount()-1
        #for f in range(9):
        #    self.resTableWidget.setItem(self.lastRowInd, 0,QTableWidgetItem())

    # Create internal dataframe with all the data.
    # This is needed for plotting data after acquisition
    def setupDataFrame(self):
        self.dfTotDeviceID = pd.DataFrame()
        self.dfTotPerfData = pd.DataFrame()
        self.dfTotAcqParams = pd.DataFrame()
        self.dfTotJV = pd.DataFrame()
    
    # Process data from devices
    def processDeviceData(self, deviceID, dfAcqParams, perfData, JV, flag, track_flag):
        # create numpy arrays for all devices as well as dataframes for csv and jsons
        self.deviceID = np.vstack((self.deviceID, np.array([deviceID])))
        self.perfData = perfData
        self.JV = JV
        
        # Populate table.
        if flag is False and track_flag is False:
            self.setupResultTable()
        self.fillTableData(deviceID, self.perfData)
        QApplication.processEvents()
        # Plot results
        self.plotData(self.deviceID,self.perfData, JV)
        
        QApplication.processEvents()
        
        if flag is True:
            # Save to internal dataFrame
            self.makeInternalDataFrames(self.lastRowInd+self.resTableWidget.rowCount() ,
                self.deviceID,self.perfData, dfAcqParams, self.JV)

            # Enable/disable saving to file
            # Using ALT with Start Acquisition button overrides the config settings.
            if self.parent().config.saveLocalCsv == True or \
                    self.parent().acquisition.modifiers == Qt.AltModifier:
                self.save_csv(deviceID, dfAcqParams, self.perfData, self.JV)
            if self.parent().config.submitToDb == True:
                self.submit_DM(deviceID, dfAcqParams, self.perfData, self.JV)

    # Plot data from devices
    def plotData(self, deviceID, perfData, JV):
        self.plotJVresp(JV)
        self.plotMPP(perfData)
        self.show()
    
    # Create internal dataframe with all the data.
    # This is needed for plotting data after acquisition
    def makeInternalDataFrames(self, index,deviceID,perfData,dfAcqParams,JV):
        self.dfTotDeviceID[index] = [deviceID]
        self.dfTotPerfData[index] = [perfData]
        self.dfTotAcqParams = self.dfTotAcqParams.append(dfAcqParams)
        self.dfTotJV[index] = [JV]
    
    # Create DataFrames for saving csv and jsons
    def makeDFPerfData(self,perfData):
        dfPerfData = pd.DataFrame({'Time step': perfData[:,2], 'Voc': perfData[:,3],
                        'Jsc': perfData[:,4], 'VPP' : perfData[:,5], 'MPP': perfData[:,6],
                        'FF': perfData[:,7], 'PCE': perfData[:,8], 'Light' : perfData[:,9],
                        'Acq Date': perfData[:,0], 'Acq Time': perfData[:,1],
                        
                                  })
        dfPerfData = dfPerfData[['Acq Date','Acq Time','Time step', 'Voc',
                                     'Jsc', 'VPP', 'MPP','FF','PCE', 'Light']]
        return dfPerfData

    def makeDFJV(self,JV,set):
        dfJV = pd.DataFrame({'V':JV[:,2*set+0], 'J':JV[:,2*set+1]})
        dfJV = dfJV[['V', 'J']]
        listJV = dict(dfJV.to_dict(orient='split'))
        listJV['columnlabel'] = listJV.pop('columns')
        listJV['output'] = listJV.pop('data')
        del listJV['index']
        return dfJV, listJV
    
    ### Submit json for device data to Data-Management
    def submit_DM(self,deviceID, dfAcqParams, perfData, JV):
        dfPerfData = self.makeDFPerfData(perfData)
        
        # Prepare json-data
        jsonData = {'itemId' : deviceID[-1]}
        listSubstrateName = {'substrate' : deviceID[:-1]}
        listEquipment = {'equipment' : 'auto-testing'}
        listAcqParams = dict(dfAcqParams.to_dict(orient='list'))

        jsonData.update(listEquipment)
        jsonData.update(listSubstrateName)
        jsonData.update(listAcqParams)

        _, listJV0 = self.makeDFJV(JV,0)
        jsonData.update(listJV0)
        if float(perfData[0,2]) == 0:
            if int(float(dfPerfData.at[0,'Light'])) == 0:
                listMeasType = {'measType' : 'JV_dark'}
                listName = {'name': 'JV_dark_f'}
                listName1 = {'name': 'JV_dark_r'}
            else:
                listMeasType = {'measType' : 'JV'}
                listName = {'name': 'JV_f'}
                listName1 = {'name': 'JV_r'}
            listPerfData = dict(dfPerfData.iloc[[0]].to_dict('list'))
            jsonData.update(listPerfData)
            jsonData.update(listName)
            jsonData.update(listMeasType)
            
            jsonData1 = jsonData.copy()
            jsonData1.update(listName1)
            listPerfData1 = dict(dfPerfData.iloc[[1]].to_dict('list'))
            jsonData1.update(listPerfData1)
            _, listJV1 = self.makeDFJV(JV,1)
            jsonData1.update(listJV1)

        else:
            listName = {'name': 'tracking'}
            listMeasType = {'measType' : 'tracking'}
            listPerfData = dict(dfPerfData.to_dict('split'))
            listPerfData['columnlabel'] = listPerfData.pop('columns')
            listPerfData['output'] = listPerfData.pop('data')
            del listPerfData['index']
            jsonData.update(listPerfData)
            jsonData.update(listName)
            jsonData.update(listMeasType)

        self.dbConnectInfo = self.parent().dbconnectionwind.getDbConnectionInfo()
        try:
            # This is for direct submission via pymongo
            conn = DataManagement(self.dbConnectInfo)
            client, _ = conn.connectDB()
            db = client[self.dbConnectInfo[2]]
            db_entry = db.Measurement.insert_one(json.loads(json.dumps(jsonData)))
            msg = " Device " + deviceID + \
                    ": submission to DM via Mongo successful\n  (ids: " + \
                    str(db_entry.inserted_id)
            if float(perfData[0,2]) == 0:
                db_entry1 = db.Measurement.insert_one(json.loads(json.dumps(jsonData1)))
                msg += ", "+str(db_entry1.inserted_id)
            msg += ")"
        except:
            try:
                msg = " Submission to DM via Mongo: failed. Trying via HTTP POST"
                print(msg)
                logger.info(msg)
                #This is for using POST HTTP
                url = "http://"+self.dbConnectInfo[0]+":"+self.dbConnectInfo[5]+self.dbConnectInfo[6]
                if float(perfData[0,2]) == 0:
                    req = requests.post(url, json=jsonData)
                    req1 = requests.post(url, json=jsonData1)
                    if req.status_code == 200 and req1.status_code == 200:
                        msg = " Device " + deviceID + \
                          ", submission to DM via HTTP POST successful\n  (ETag: " + \
                          str(req.headers['ETag'])+", "+str(req1.headers['ETag'])+")"
                    else:
                        req.raise_for_status()
                        req1.raise_for_status()
                else:
                    if req.status_code == 200:
                        req = requests.post(url, json=jsonData)
                        msg = " Device " + deviceID + \
                          ", submission to DM via HTTP POST successful\n  (ETag: " + \
                          str(req.headers['ETag'])+")"
                    else:
                        req.raise_for_status()
            except:
                msg = " Connection to DM server: failed. Saving local file"
                self.save_csv(deviceID, dfAcqParams, perfData, JV)
        print(msg)
        logger.info(msg)
        
    # Open DM window for searching for data in DM
    def openWindowDM(self, deviceID):
        self.loadDMWindow = DataLoadDMWindow(parent=self)
        self.loadDMWindow.show()
        deviceID = self.loadDMWindow.deviceData.connect(lambda deviceID, perfData, JV:\
            self.loadDeviceDM(deviceID, perfData, JV))
    
    # Once data is retrieved from DM, plot it and populate table
    def loadDeviceDM(self, deviceID, perfData, JV):
        print(" Plotting data for:",deviceID)
        self.plotData(deviceID, perfData, JV)
        self.setupResultTable()
        self.fillTableData(deviceID, perfData)

    # Load data from saved CSV
    def load_csv(self):
        filenames = QFileDialog.getOpenFileNames(self,
                        "Open csv data", "","*.csv")
        try:
            for filename in filenames[0]:
                print("Open saved device data from: ", filename)
                dftot = pd.read_csv(filename, na_filter=False)
                deviceID = dftot.at[0,'Device']
                perfData = dftot.values[range(0,np.count_nonzero(dftot['Acq Date']))][:,range(1,11)]
                JV = dftot.values[range(0,np.count_nonzero(dftot['V_r']))][:,np.arange(11,15)].astype(float)
                dfAcqParams = dftot.loc[0:1, 'Acq Soak Voltage':'Comments']
                self.plotData(deviceID, perfData, JV)
                self.setupResultTable()
                self.fillTableData(deviceID, perfData)
                self.makeInternalDataFrames(self.resTableWidget.rowCount()-1, [[deviceID]], perfData, dfAcqParams, np.array(JV))
        except:
            print("Loading files failed")

    # Save device acquisition as csv
    def save_csv(self,deviceID, dfAcqParams, perfData, JV):
        dfPerfData = self.makeDFPerfData(perfData)
        dfJV0,_ = self.makeDFJV(JV,0)
        dfJV1,_ = self.makeDFJV(JV,1)
        dfJV0 = dfJV0.rename(columns={"V": "V_f", "J": "J_f"})
        dfJV1 = dfJV1.rename(columns={"V": "V_r", "J": "J_r"})
    
        dfDeviceID = pd.DataFrame({'Device':[deviceID]})
        dfTot = pd.concat([dfDeviceID, dfPerfData], axis = 1)
        dfTot = pd.concat([dfTot,dfJV0], axis = 1)
        dfTot = pd.concat([dfTot,dfJV1], axis = 1)
        dfTot = pd.concat([dfTot,dfAcqParams], axis = 1)
        dateTimeTag = str(datetime.now().strftime('%Y%m%d-%H%M%S'))
        csvFilename = deviceID+"_"
        if int(float(dfPerfData.at[0,'Light'])) == 0:
            csvFilename+="dark_"
        if int(float(dfPerfData.at[0,'Light'])) != 0:
            if float(perfData[0,2]) != 0:
                csvFilename += "tracking_"
        csvFilename += dateTimeTag + ".csv"
        try:
            dfTot.to_csv(self.csvFolder+"/"+csvFilename, sep=',', index=False)
            msg=" Device data saved on: "+self.csvFolder+"/"+csvFilename
        except:
            msg=" Device data NOT saved. Check File saving folder in INI file"
        print(msg)
        logger.info(msg)

    # Populate result table.
    def fillTableData(self, deviceID, obj):
        if str(obj[0,9]) == "1.0":
            light = "ON"
        else:
            light = "OFF"
        
        self.resTableWidget.setItem(self.lastRowInd, 0,QTableWidgetItem(deviceID))
        
        for i in range(1,7,1):
            self.resTableWidget.setItem(self.lastRowInd, i,QTableWidgetItem("{0:0.3f}".format(np.mean(obj[:,i+2].astype(float)))))
            try:
                self.resTableWidget.item(self.lastRowInd,i).setToolTip("F:{0:0.3f}".format(float(obj[0,i+2]))+" / B:{0:0.3f}".format(float(obj[1,i+2])))
            except:
                pass
        self.resTableWidget.setItem(self.lastRowInd, 7,QTableWidgetItem(light)) #Light
        self.resTableWidget.setItem(self.lastRowInd, 9,QTableWidgetItem(obj[0,0]))
        self.resTableWidget.setItem(self.lastRowInd, 10,QTableWidgetItem(obj[0,1]))
        
        if float(obj[0,2]) == 0.:
            self.resTableWidget.setItem(self.lastRowInd, 8,QTableWidgetItem("None")) #track_time
        else:
            self.resTableWidget.setItem(self.lastRowInd, 8,QTableWidgetItem("{0:0.3f}".format(float(obj[0,2])))) #track_time

####################################################################
#   Custom Toolbar with linear/log button
####################################################################
class CustomToolbar(NavigationToolbar):
    def __init__(self, figure_canvas, figure, parent= None):
        self.figure = figure
        self.figure_canvas = figure_canvas
        self.toolitems +=(('Log/Lin', "Log/Lin scale", "Log/Lin scale", 'log_lin_scale'),)
        NavigationToolbar.__init__(self, figure_canvas, parent=parent)

    def log_lin_scale(self):
        if len(self.figure.gca().lines) > 2:
            if self.figure.gca().get_yscale() == 'log':
                self.figure.gca().set_yscale('linear')
            else:
                self.figure.gca().set_yscale('log')
            self.figure_canvas.draw()

####################################################################
#   Window for data loading form DM
####################################################################
class DataLoadDMWindow(QMainWindow):
    deviceData = pyqtSignal(str, np.ndarray, np.ndarray)

    def __init__(self, parent=None):
        super(DataLoadDMWindow, self).__init__(parent)
        self.title = 'Open Data from DM'
        self.deviceID = ""
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(QRect(10, 30, 360, 320))
        self.textbox = QLineEdit(self)
        self.textbox.setGeometry(QRect(15, 15, 180, 30))
        self.textbox.setToolTip("Ex: NF190203AA")
        self.textbox.setText("")
        self.button = QPushButton('Search DM', self)
        self.button.setGeometry(QRect(205, 15, 100, 30))
        
        self.resTableDMWidget = QTableWidget(self)
        self.resTableDMWidget.setGeometry(QRect(10, 60, 340, 240))
        #self.resTableDMWidget.setItem(0,0, QTableWidgetItem(""))
        self.resTableDMWidget.setColumnCount(3)
        self.resTableDMWidget.setHorizontalHeaderItem(0,QTableWidgetItem("Device ID"))
        self.resTableDMWidget.setHorizontalHeaderItem(1,QTableWidgetItem("Device"))
        self.resTableDMWidget.setHorizontalHeaderItem(2,QTableWidgetItem("Type"))
        self.resTableDMWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.resTableDMWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.lastRowInd=0
        self.resTableDMWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.button.clicked.connect(self.onSearchButtonClick)
        self.resTableDMWidget.itemDoubleClicked.connect(self.onTableEntryClick)
        self.show()
    
    # Get list of devices data from DM
    @pyqtSlot()
    def onSearchButtonClick(self):
        self.deviceID = self.textbox.text()
        self.textbox.setText("")
        db, connFlag = self.connectDM()
        if connFlag == False:
            print("Abort")
            return
        #print(" Number of Measurement entries: ",db.Measurement.find({'substrate':self.deviceID}).count())
        try:
            for cursor in db.Measurement.find({'substrate':self.deviceID}):
                self.resTableDMWidget.insertRow(0)
                self.resTableDMWidget.setItem(0, 0,QTableWidgetItem(self.deviceID))
                self.resTableDMWidget.setItem(0, 1,QTableWidgetItem(cursor['itemId']))
                if cursor['measType'] == "JV":
                    self.resTableDMWidget.setItem(0, 2,QTableWidgetItem("JV"))
                elif cursor['measType'] == "JV_dark":
                    self.resTableDMWidget.setItem(0, 2,QTableWidgetItem("JV_dark"))
                elif cursor['measType'] == "tracking":
                    self.resTableDMWidget.setItem(0, 2,QTableWidgetItem("tracking"))
        
                self.resTableDMWidget.item(0,0).setToolTip("Double click to plot data")
                QApplication.processEvents()
        except:
            print(" Error in reading from DM. Aborting")
            
    # Get specific device data from DM and push it back to parent for plotting
    @pyqtSlot()
    def onTableEntryClick(self):
        substrate = self.resTableDMWidget.selectedItems()[0].text()
        device = self.resTableDMWidget.selectedItems()[1].text()
        type = self.resTableDMWidget.selectedItems()[2].text()
        db, connFlag = self.connectDM()
        if connFlag == False:
            print("Abort")
            return
        if type == "JV" or type == "JV_dark":
            for entry in db.Measurement.find({'substrate':substrate, 'itemId':device}):
                if entry['measType'] == "JV":
                    if entry['name'] == "JV_r":
                        entryR = entry
                    if entry['name'] == "JV_f":
                        entryF = entry
                elif entry['measType'] == "JV_dark":
                    if entry['name'] == "JV_dark_r":
                        entryR = entry
                    if entry['name'] == "JV_dark_f":
                        entryF = entry
        
            perfData = np.array([self.getPerfData(entryR),self.getPerfData(entryF)])

            JV_r = self.getJV(entryR)
            JV_f = self.getJV(entryF)
            JV = np.append(JV_r,JV_f,axis=1)

        elif type == "tracking":
            for entry in db.Measurement.find({'substrate':substrate, 'itemId':device, 'measType':'tracking'}):
                perfData = np.array(entry['output'])
                JV = np.array([[0., 0., 0., 0.]])
        try:
            self.deviceData.emit(substrate+device, perfData, JV)
        except:
            print(" Failed to load file from DM.")

    # Process entry from DM into perfData
    def getPerfData(self,entry):
        perfData = np.append(entry['Acq Date'],entry['Acq Time'])
        perfData = np.append(perfData,entry['Time step'])
        perfData = np.append(perfData,entry['Voc'])
        perfData = np.append(perfData,entry['Jsc'])
        perfData = np.append(perfData,entry['VPP'])
        perfData = np.append(perfData,entry['MPP'])
        perfData = np.append(perfData,entry['FF'])
        perfData = np.append(perfData,entry['PCE'])
        perfData = np.append(perfData,entry['Light'])
        return perfData
    
    # Format JV data from DM
    def getJV(self,entry):
        JV = np.array(entry['output'])
        return JV

    # Connect to DM
    def connectDM(self):
        self.dbConnectInfo = self.parent().parent().dbconnectionwind.getDbConnectionInfo()
        try:
            conn = DataManagement(self.dbConnectInfo)
            client, _ = conn.connectDB()
            db = client[self.dbConnectInfo[2]]
            #print(" Connected to DM")
            return db, True
        except:
            print(" Connection to DM failed")
            return None, False
