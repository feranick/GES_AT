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
from PyQt5.QtCore import (QRect,pyqtSlot)
from PyQt5.QtGui import QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

from . import config

'''
   Results Window
'''
class ResultsWindow(QMainWindow):
    def __init__(self):
        super(ResultsWindow, self).__init__()
        self.deviceID = np.zeros((0,1))
        self.perfData = np.ones((0,5))
        self.JV = np.array([])
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
        self.resTableWidget.setColumnCount(5)
        self.resTableWidget.setRowCount(0)
        self.resTableWidget.setItem(0,0, QTableWidgetItem(""))
        self.resTableWidget.setHorizontalHeaderItem(0,QTableWidgetItem("Device ID"))
        self.resTableWidget.setHorizontalHeaderItem(1,QTableWidgetItem("Av Voc [V]"))
        self.resTableWidget.setHorizontalHeaderItem(2,QTableWidgetItem("Av Jsc [mA/cm^2]"))
        self.resTableWidget.setHorizontalHeaderItem(3,QTableWidgetItem("Av FF"))
        self.resTableWidget.setHorizontalHeaderItem(4,QTableWidgetItem("Time"))

        self.resTableWidget.itemClicked.connect(self.onCellClick)

        # Make Menu for plot related calls
        self.setCentralWidget(self.centralwidget)
        self.openMenu = QAction("&Open Data", self)
        self.openMenu.setShortcut("Ctrl+o")
        self.openMenu.setStatusTip('Plot data from saved file')
        self.openMenu.triggered.connect(self.open_data)
        self.clearMenu = QAction("&Clear Plots", self)
        self.clearMenu.setShortcut("Ctrl+x")
        self.clearMenu.setStatusTip('Clear plots')
        self.clearMenu.triggered.connect(self.clearPlots)
        
        self.menuBar = QMenuBar(self)
        plotMenu = self.menuBar.addMenu('&Plot')
        plotMenu.addAction(self.openMenu)
        plotMenu.addSeparator()
        plotMenu.addAction(self.clearMenu)

        self.statusbar = QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

    
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
        self.lineMPP.set_data(data[:,0], data[:,4])
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
    def clearPlots(self):
        self.deviceID = np.zeros((0,1))
        self.perfData = np.zeros((0,5))
        self.JV = np.array([])
        self.initPlots(self.perfData)
        self.initJVPlot()
        self.resTableWidget.setRowCount(0)
        QApplication.processEvents()
    
    # Action upon selecting a row in the table.
    @pyqtSlot()
    def onCellClick(self):
        row = self.resTableWidget.selectedItems()[0].row()
        for j in range(self.resTableWidget.columnCount()):
            for i in range(self.resTableWidget.rowCount()):
                self.resTableWidget.item(i,j).setBackground(QColor(255,255,255))
  
        self.plotData(self.deviceID,self.perfData, self.JV[row])
        for j in range(self.resTableWidget.columnCount()):
            self.resTableWidget.item(row,j).setBackground(QColor(0,255,0))

    def setupResultTable(self):
        # Add row and initialize it within the table
        self.resTableWidget.insertRow(self.resTableWidget.rowCount())
        self.resTableWidget.setItem(self.resTableWidget.rowCount()-1,0,QTableWidgetItem())
        for j in range(self.resTableWidget.columnCount()):
            self.resTableWidget.setItem(self.resTableWidget.rowCount(),j,QTableWidgetItem())
        self.lastRowInd = self.resTableWidget.rowCount() - 1
        
    def setupDataFrame(self):
        self.dfTotDeviceID = pd.DataFrame()
        self.dfTotPerfData = pd.DataFrame()
        self.dfTotJV = pd.DataFrame()
    
    ###### Processing #############
    def processDeviceData(self, deviceID, dfAcqParams, perfData, JV):
    
        # create numpy arrays for all devices as well as dataframes for csv and jsons
        self.deviceID = np.vstack((self.deviceID, np.array([deviceID])))
        self.perfData = np.vstack((self.perfData, np.array([perfData])))
        
        if self.JV.shape[0] == 0:
            self.JV.resize((0,JV.shape[0],2))
        self.JV = np.vstack([self.JV,[JV]])


        # Populate table.
        self.resTableWidget.setItem(self.lastRowInd, 0,QTableWidgetItem(deviceID))
        self.resTableWidget.setItem(self.lastRowInd, 1,QTableWidgetItem("{0:0.3f}".format(np.mean(self.perfData[:,1]))))
        self.resTableWidget.setItem(self.lastRowInd, 2,QTableWidgetItem("{0:0.3f}".format(np.mean(self.perfData[:,2]))))
        self.resTableWidget.setItem(self.lastRowInd, 3,QTableWidgetItem("{0:0.3f}".format(np.mean(self.perfData[:,3]))))
        self.resTableWidget.setItem(self.lastRowInd, 4,QTableWidgetItem("{0:0.3f}".format(np.mean(self.perfData[:,0]))))
        
        
        QApplication.processEvents()
        # Plot results
        self.plotData(self.deviceID,self.perfData, self.JV[self.lastRowInd])
        QApplication.processEvents()
        
        dfPerfData = self.makeDFPerfData(self.perfData)
        dfJV = self.makeDFJV(self.JV[self.lastRowInd])
        
        self.save_csv(deviceID, dfAcqParams, dfPerfData, dfJV, self.lastRowInd)
        self.save_json(deviceID, dfAcqParams, dfPerfData, dfJV, self.lastRowInd)
        

    def plotData(self, deviceID, perfData, JV):
        self.plotJVresp(JV)
        self.plotTVoc(perfData)
        self.plotMPP(perfData)
        self.plotTJsc(perfData)
        self.show()

    def makeInternalDataFrames(self, index):
        self.dfTotDeviceID = self.dfTotDeviceID.append(pd.DataFrame({index: [self.deviceID]}))
        self.dfTotPerfData = self.dfTotPerfData.append(pd.DataFrame({index: [self.perfData]}))
        self.dfTotJV = self.dfTotJV.append(pd.DataFrame({index: [self.JV]}))
        print(self.dfTotDeviceID)
        print(self.dfTotPerfData)
        print(self.dfTotJV)


    ### Create DataFrames for saving csv and jsons
    def makeDFPerfData(self,perfData):
        dfPerfData = pd.DataFrame({'time': perfData[:,0], 'Voc': perfData[:,1], 'Jsc': perfData[:,2], 'MPP': perfData[:,3]})
        dfPerfData = dfPerfData[['time', 'Voc', 'Jsc', 'MPP']]
        return dfPerfData
    
    def makeDFJV(self,JV):
        dfJV = pd.DataFrame({'V':JV[:,0], 'J':JV[:,1]})
        dfJV = dfJV[['V', 'J']]
        return dfJV

    ### Save device acquisition as csv
    def save_csv(self,deviceID, dfAcqParams, dfPerfData, dfJV, index):
        dfDeviceID = pd.DataFrame({'device':[deviceID]})
        dfTot = pd.concat([dfDeviceID, dfPerfData], axis = 1)
        dfTot = pd.concat([dfTot,dfJV], axis = 1)
        dfTot = pd.concat([dfTot,dfAcqParams], axis = 1)
        csvFilename = str(dfDeviceID.get_value(0,'device'))+"_"+str(int(dfPerfData.get_value(index,'time')))+".csv"
        dfTot.to_csv(csvFilename, sep=',', index=False)
        print("Device data saved on: ",csvFilename)
    
    ### Prepare json for device data
    def save_json(self,deviceID, dfAcqParams, dfPerfData, dfJV, index):
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

    ### Open JV from file
    def open_data(self):
        filenames = QFileDialog.getOpenFileNames(self,
                        "Open ASCII JV data", "","*.txt")
        try:
            for filename in filenames:
                data = open(filename)
                M = np.loadtxt(data,unpack=False)
                self.plotJVresp(M)
        except:
            print("Loading files failed")
