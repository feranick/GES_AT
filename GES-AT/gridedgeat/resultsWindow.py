'''
ResultsWindow.py
-------------
Classes for providing a graphical user interface
for the resultsWindow

Copyright (C) 2017 Nicola Ferralis <ferralis@mit.edu>
Copyright (C) 2017 Auto-testing team - MIT GridEdge Solar

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

'''

import sys, random, math, json
import numpy as np
import pandas as pd
from datetime import datetime
from PyQt5.QtWidgets import (QMainWindow,QPushButton,QVBoxLayout,QFileDialog,QWidget, QGridLayout,QGraphicsView,QLabel,QComboBox,QLineEdit,QMenuBar,QStatusBar, QApplication,QTableWidget,QTableWidgetItem,QAction)
from PyQt5.QtCore import (QRect,pyqtSlot,Qt)
from PyQt5.QtGui import (QColor)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

from . import config
from .dataManagement import *
from . import logger

'''
   Results Window
'''
class ResultsWindow(QMainWindow):
    def __init__(self, parent=None):
        super(ResultsWindow, self).__init__(parent)
        self.deviceID = np.zeros((0,1))
        self.perfData = np.ones((0,5))
        self.JV = np.array([])
        self.setupDataFrame()
        self.csvFolder = config.csvSavingFolder
        self.initUI()
        self.initPlots(self.perfData)
        self.initJVPlot()
    
    def initUI(self):
        self.setGeometry(500, 100, 1150, 950)
        self.setWindowTitle('Results Panel')
        
        # a figure instance to plot on
        self.figureTJsc = plt.figure()
        self.figureTVoc = plt.figure()
        self.figureJVresp = plt.figure()
        self.figureMPP = plt.figure()
        self.figureTJsc.subplots_adjust(left=0.15, right=0.95, top=0.95, bottom=0.21)
        self.figureTVoc.subplots_adjust(left=0.15, right=0.95, top=0.95, bottom=0.21)
        self.figureJVresp.subplots_adjust(left=0.15, right=0.85, top=0.95, bottom=0.21)
        self.figureMPP.subplots_adjust(left=0.15, right=0.95, top=0.95, bottom=0.21)

        self.centralwidget = QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayoutWidget = QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QRect(20, 30, 1100, 710))
        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        
        self.canvasTJsc = FigureCanvas(self.figureTJsc)
        self.gridLayout.addWidget(self.canvasTJsc, 1, 0, 1, 1)
        self.canvasTVoc = FigureCanvas(self.figureTVoc)
        self.gridLayout.addWidget(self.canvasTVoc, 1, 1, 1, 1)
        self.canvasJVresp = FigureCanvas(self.figureJVresp)
        self.gridLayout.addWidget(self.canvasJVresp, 3, 0, 1, 1)
        self.canvasMPP = FigureCanvas(self.figureMPP)
        self.gridLayout.addWidget(self.canvasMPP, 3, 1, 1, 1)
        
        self.toolbarTJsc = NavigationToolbar(self.canvasTJsc, self)
        self.gridLayout.addWidget(self.toolbarTJsc, 0, 0, 1, 1)
        self.toolbarTVoc = NavigationToolbar(self.canvasTVoc, self)
        self.gridLayout.addWidget(self.toolbarTVoc, 0, 1, 1, 1)
        self.toolbarJVresp = NavigationToolbar(self.canvasJVresp, self)
        self.gridLayout.addWidget(self.toolbarJVresp, 2, 0, 1, 1)
        self.toolbarMPP = NavigationToolbar(self.canvasMPP, self)
        self.gridLayout.addWidget(self.toolbarMPP, 2, 1, 1, 1)

        self.resTableWidget = QTableWidget(self.centralwidget)
        self.resTableWidget.setGeometry(QRect(20, 770, 1100, 145))
        self.resTableWidget.setColumnCount(6)
        self.resTableWidget.setRowCount(0)
        self.resTableWidget.setItem(0,0, QTableWidgetItem(""))
        self.resTableWidget.setHorizontalHeaderItem(0,QTableWidgetItem("Device ID"))
        self.resTableWidget.setHorizontalHeaderItem(1,QTableWidgetItem("Av Voc [V]"))
        self.resTableWidget.setHorizontalHeaderItem(2,QTableWidgetItem("Av Jsc [mA/cm^2]"))
        self.resTableWidget.setHorizontalHeaderItem(3,QTableWidgetItem("MPP [mW/cm^2]"))
        self.resTableWidget.setHorizontalHeaderItem(4,QTableWidgetItem("Av FF"))
        self.resTableWidget.setHorizontalHeaderItem(5,QTableWidgetItem("Time"))

        self.resTableWidget.itemClicked.connect(self.onCellClick)
        self.setCentralWidget(self.centralwidget)

        # Make Menu for plot related calls
        self.menuBar = QMenuBar(self)

        self.loadMenu = QAction("&Load Data", self)
        self.loadMenu.setShortcut("Ctrl+o")
        self.loadMenu.setStatusTip('Load csv data from saved file')
        self.loadMenu.triggered.connect(self.read_csv)
        self.directoryMenu = QAction("&Set saving directory", self)
        self.directoryMenu.setShortcut("Ctrl+s")
        self.directoryMenu.setStatusTip('Set directory for saved files')
        self.directoryMenu.triggered.connect(self.set_dir_saved)
        
        self.clearMenu = QAction("&Clear Plots", self)
        self.clearMenu.setShortcut("Ctrl+x")
        self.clearMenu.setStatusTip('Clear plots')
        self.clearMenu.triggered.connect(lambda: self.clearPlots(True))
        
        fileMenu = self.menuBar.addMenu('&File')
        fileMenu.addAction(self.loadMenu)
        fileMenu.addAction(self.directoryMenu)
        plotMenu = self.menuBar.addMenu('&Plot')
        plotMenu.addAction(self.clearMenu)
        
        self.parent().viewWindowMenus(self.menuBar, self.parent())
        
        self.statusbar = QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

    def set_dir_saved(self):
        self.csvFolder = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        msg = "CSV Files will be saved in: "+self.csvFolder
        print(msg)
        logger.info(msg)
    
    def plotSettings(self, ax):
        ax.tick_params(axis='both', which='major', labelsize=5)
        ax.tick_params(axis='both', which='minor', labelsize=5)
    
    # Initialize Time-based plots
    def initPlots(self, data):
        self.figureTJsc.clf()
        self.axTJsc = self.figureTJsc.add_subplot(111)
        self.plotSettings(self.axTJsc)
        self.axTJsc.set_xlabel('Time [s]',fontsize=5)
        self.axTJsc.set_ylabel('Jsc [mA/cm^2]',fontsize=5)
        self.axTJsc.set_autoscale_on(True)
        self.axTJsc.autoscale_view(True,True,True)
        self.canvasTJsc.draw()
        self.lineTJsc, = self.axTJsc.plot(data[:,0],data[:,2], '.-',linewidth=0.5)
        
        self.figureTVoc.clf()
        self.axTVoc = self.figureTVoc.add_subplot(111)
        self.plotSettings(self.axTVoc)
        self.axTVoc.set_xlabel('Time [s]',fontsize=5)
        self.axTVoc.set_ylabel('Voc [V]',fontsize=5)
        self.axTVoc.set_autoscale_on(True)
        self.axTVoc.autoscale_view(True,True,True)
        self.canvasTVoc.draw()
        self.lineTVoc, = self.axTVoc.plot(data[:,0],data[:,1], '.-',linewidth=0.5)
        
        self.figureMPP.clf()
        self.axMPP = self.figureMPP.add_subplot(111)
        self.plotSettings(self.axMPP)
        self.axMPP.set_xlabel('Time [s]',fontsize=5)
        self.axMPP.set_ylabel('Max power point [mW]',fontsize=5)
        self.axMPP.set_autoscale_on(True)
        self.axMPP.autoscale_view(True,True,True)
        self.canvasMPP.draw()
        self.lineMPP, = self.axMPP.plot(data[:,0],data[:,4], '.-',linewidth=0.5)
    
    # Initialize JV and PV plots
    def initJVPlot(self):
        self.figureJVresp.clf()
        self.axJVresp = self.figureJVresp.add_subplot(111)
        self.axPVresp = self.axJVresp.twinx()
        self.plotSettings(self.axJVresp)
        self.plotSettings(self.axPVresp)
        self.axJVresp.set_xlabel('Voltage [V]',fontsize=5)
        self.axJVresp.set_ylabel('Current density [mA/cm^2]',fontsize=5)
        self.axPVresp.set_ylabel('Power density [mW/cm^2]',fontsize=5)
        self.canvasJVresp.draw()

    # Plot Transient Jsc
    def plotTJsc(self, data):
        self.lineTJsc.set_data(data[:,0], data[:,2])
        self.axTJsc.relim()
        self.axTJsc.autoscale_view(True,True,True)
        self.canvasTJsc.draw()
    
    # Plot Transient Voc
    def plotTVoc(self, data):
        self.lineTVoc.set_data(data[:,0], data[:,1])
        self.axTVoc.relim()
        self.axTVoc.autoscale_view(True,True,True)
        self.canvasTVoc.draw()

    # Plot MPP with tracking
    def plotMPP(self, data):
        self.lineMPP.set_data(data[:,0], data[:,3])
        self.axMPP.relim()
        self.axMPP.autoscale_view(True,True,True)
        self.canvasMPP.draw()
    
    # Plot JV response
    def plotJVresp(self, JV):
        self.initJVPlot()
        self.axJVresp.plot(JV[:,0],JV[:,1], '.-',linewidth=0.5)
        self.axPVresp.plot(JV[:,0],JV[:,0]*JV[:,1], '.-',linewidth=0.5,
                color='orange')
        self.canvasJVresp.draw()
    
    # Clear all plots and fields
    def clearPlots(self, includeTable):
        self.deviceID = np.zeros((0,1))
        self.perfData = np.zeros((0,5))
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
                
        self.plotData(self.dfTotDeviceID.get_value(0,row),
                self.dfTotPerfData.get_value(0,row),
                self.dfTotJV.get_value(0,row)[self.dfTotJV.get_value(0,row).shape[0]-1])

    # Add row and initialize it within the table
    def setupResultTable(self):
        self.resTableWidget.insertRow(self.resTableWidget.rowCount())
        self.resTableWidget.setItem(self.resTableWidget.rowCount()-1,0,QTableWidgetItem())
        for j in range(self.resTableWidget.columnCount()):
            self.resTableWidget.setItem(self.resTableWidget.rowCount(),j,QTableWidgetItem())
        self.lastRowInd = self.resTableWidget.rowCount()-1

    # Create internal dataframe with all the data. This is needed for plotting data after acquisition
    def setupDataFrame(self):
        self.dfTotDeviceID = pd.DataFrame()
        self.dfTotPerfData = pd.DataFrame()
        self.dfTotJV = pd.DataFrame()
    
    # Process data from devices
    def processDeviceData(self, deviceID, dfAcqParams, perfData, JV):
    
        # create numpy arrays for all devices as well as dataframes for csv and jsons
        self.deviceID = np.vstack((self.deviceID, np.array([deviceID])))
        self.perfData = np.vstack((self.perfData, np.array([perfData])))
        
        if self.JV.shape[0] == 0:
            self.JV.resize((0,JV.shape[0],2))
        self.JV = np.vstack([self.JV,[JV]])
        
        # Populate table.
        self.fillTableData(deviceID, self.perfData)
     
        QApplication.processEvents()
        # Plot results
        self.plotData(self.deviceID,self.perfData, JV)
        QApplication.processEvents()
        
        dfPerfData = self.makeDFPerfData(self.perfData)
        dfJV = self.makeDFJV(self.JV[self.JV.shape[0]-1])
        
        if config.saveLocalCsv is True:
            self.save_csv(deviceID, dfAcqParams, dfPerfData, dfJV)

        self.submit_DM(self.make_json(deviceID, dfAcqParams, dfPerfData, dfJV))
        
    # Plot data from devices
    def plotData(self, deviceID, perfData, JV):
        self.plotJVresp(JV)
        self.plotTVoc(perfData)
        self.plotMPP(perfData)
        self.plotTJsc(perfData)
        self.show()
    
    # Create internal dataframe with all the data. This is needed for plotting data after acquisition
    def makeInternalDataFrames(self, index,deviceID,perfData,JV):
        self.dfTotDeviceID[index] = [deviceID]
        self.dfTotPerfData[index] = [perfData]
        self.dfTotJV[index] = [JV]
    
    # Create DataFrames for saving csv and jsons
    def makeDFPerfData(self,perfData):
        dfPerfData = pd.DataFrame({'time': perfData[:,0], 'Voc': perfData[:,1],
                        'Jsc': perfData[:,2], 'MPP': perfData[:,3],
                        'FF': perfData[:,4]})
        dfPerfData = dfPerfData[['time', 'Voc', 'Jsc', 'MPP','FF']]
        return dfPerfData
    
    def makeDFJV(self,JV):
        dfJV = pd.DataFrame({'V':JV[:,0], 'J':JV[:,1]})
        dfJV = dfJV[['V', 'J']]
        return dfJV

    ### Save device acquisition as csv
    def save_csv(self,deviceID, dfAcqParams, dfPerfData, dfJV):
        dfDeviceID = pd.DataFrame({'device':[deviceID]})
        dfTot = pd.concat([dfDeviceID, dfPerfData], axis = 1)
        dfTot = pd.concat([dfTot,dfJV], axis = 1)
        dfTot = pd.concat([dfTot,dfAcqParams], axis = 1)
        csvFilename = str(dfDeviceID.get_value(0,'device'))+".csv"
        dfTot.to_csv(self.csvFolder+"/"+csvFilename, sep=',', index=False)
        msg=" Device data saved on: "+self.csvFolder+"/"+csvFilename
        print(msg)
        logger.info(msg)
    
    ### Prepare json for device data
    def make_json(self,deviceID, dfAcqParams, dfPerfData, dfJV):
        dfDeviceID = pd.DataFrame({'device':[deviceID]})
        listTot = dict(dfDeviceID.to_dict(orient='list'))
        listAcqParams = dict(dfAcqParams.to_dict(orient='list'))
        listPerfData = dict(dfPerfData.to_dict(orient='list'))
        listJV = dict(dfJV.to_dict(orient='list'))
        
        listTot.update(listPerfData)
        listTot.update(listJV)
        listTot.update(listAcqParams)
        jsonTot = json.dumps(listTot)
        return jsonTot
    
    ### Submit json for device data to Data-Management
    def submit_DM(self,jsonData):
        self.dbConnectInfo = self.parent().dbconnectionwind.getDbConnectionInfo()
        conn = DataManagement(self.dbConnectInfo)
        client, _ = conn.connectDB()
        db = client[self.dbConnectInfo[2]]
        try:
            db_entry = db.EnvTrack.insert_one(json.loads(jsonData))
            msg = " Submission to DM: successful (id:"+str(db_entry.inserted_id)+")\n"
            print(msg)
            logger.info(msg)
        except:
            msg = " Submission to DM: failed.\n"
            print(msg)
            logger.info(msg)

    ### Load data from saved CSV
    def read_csv(self):
        filenames = QFileDialog.getOpenFileNames(self,
                        "Open csv data", "","*.csv")
        try:
            for filename in filenames[0]:
                print("Open saved device data from: ", filename)
                dftot = pd.read_csv(filename, na_filter=False)
                self.deviceID = dftot.get_value(0,'device')
                self.perfData = dftot.as_matrix()[range(0,np.count_nonzero(dftot['time']))][:,range(1,6)]
                self.JV = dftot.as_matrix()[range(0,np.count_nonzero(dftot['V']))][:,np.arange(6,8)]
                self.plotData(self.deviceID, self.perfData,self.JV)
        
                self.setupResultTable()
                self.fillTableData(self.deviceID, self.perfData)
                self.makeInternalDataFrames(self.lastRowInd, self.deviceID, self.perfData, np.array([self.JV]))
        except:
            print("Loading files failed")

    # Populate table.
    def fillTableData(self, deviceID, obj):
        self.resTableWidget.setItem(self.lastRowInd, 0,QTableWidgetItem(deviceID))
        self.resTableWidget.setItem(self.lastRowInd, 1,QTableWidgetItem("{0:0.3f}".format(np.mean(obj[:,1].astype(float)))))
        self.resTableWidget.setItem(self.lastRowInd, 2,QTableWidgetItem("{0:0.3f}".format(np.mean(obj[:,2].astype(float)))))
        self.resTableWidget.setItem(self.lastRowInd, 3,QTableWidgetItem("{0:0.3f}".format(np.mean(obj[:,3].astype(float)))))
        self.resTableWidget.setItem(self.lastRowInd, 4,QTableWidgetItem("{0:0.3f}".format(np.mean(obj[:,4].astype(float)))))
        self.resTableWidget.setItem(self.lastRowInd, 5,QTableWidgetItem("{0:0.3f}".format(np.mean(obj[:,0].astype(float)))))

