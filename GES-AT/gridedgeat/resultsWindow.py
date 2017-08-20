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

import sys, random, math
import numpy as np
from datetime import datetime
from PyQt5.QtWidgets import (QMainWindow,QPushButton,QVBoxLayout,QFileDialog,QWidget, QGridLayout,QGraphicsView,QLabel,QComboBox,QLineEdit,QMenuBar,QStatusBar, QApplication,QTableWidget,QTableWidgetItem)
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
        self.initUI()
        self.summaryData = np.zeros((0,5))
        self.initPlots(self.summaryData)
        self.initJVPlot()
        self.time = 0  #### This will be removed once testing of random plotting is done
    
    def initUI(self):
        self.setGeometry(500, 100, 1150, 925)
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
        self.gridLayoutWidget.setGeometry(QRect(20, 40, 1100, 710))
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

        '''
        self.deviceIDLabel = QLabel(self.centralwidget)
        self.deviceIDLabel.setGeometry(QRect(30, 10, 125, 30))
        self.deviceIDLabel.setObjectName("deviceIDLabel")
        self.deviceIDCBox = QComboBox(self.centralwidget)
        self.deviceIDCBox.setGeometry(QRect(150, 10, 300, 25))
        self.deviceIDCBox.setObjectName("deviceIDCBox")
        self.gridLayoutWidget_2 = QWidget(self.centralwidget)
        self.gridLayoutWidget_2.setGeometry(QRect(150, 770, 721, 111))
        self.gridLayout_2 = QGridLayout(self.gridLayoutWidget_2)
        self.gridLayout_2.setContentsMargins(10, 10, 10, 10)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.avJscText = QLineEdit(self.gridLayoutWidget_2)
        self.avJscText.setObjectName("avJscText")
        self.gridLayout_2.addWidget(self.avJscText, 0, 1, 1, 1)
        self.corrJscText = QLineEdit(self.gridLayoutWidget_2)
        self.corrJscText.setObjectName("corrJscText")
        self.gridLayout_2.addWidget(self.corrJscText, 0, 3, 1, 1)
        self.avJscLabel = QLabel(self.gridLayoutWidget_2)
        self.avJscLabel.setObjectName("avJscLabel")
        self.gridLayout_2.addWidget(self.avJscLabel, 0, 0, 1, 1)
        self.corrVocLabel = QLabel(self.gridLayoutWidget_2)
        self.corrVocLabel.setObjectName("corrVocLabel")
        self.gridLayout_2.addWidget(self.corrVocLabel, 1, 2, 1, 1)
        self.corrJscLabel = QLabel(self.gridLayoutWidget_2)
        self.corrJscLabel.setObjectName("corrJscLabel")
        self.gridLayout_2.addWidget(self.corrJscLabel, 0, 2, 1, 1)
        self.corrFFLabel = QLabel(self.gridLayoutWidget_2)
        self.corrFFLabel.setObjectName("corrFFLabel")
        self.gridLayout_2.addWidget(self.corrFFLabel, 2, 2, 1, 1)
        self.avVocLabel = QLabel(self.gridLayoutWidget_2)
        self.avVocLabel.setObjectName("avVocLabel")
        self.gridLayout_2.addWidget(self.avVocLabel, 1, 0, 1, 1)
        self.avFFLabel = QLabel(self.gridLayoutWidget_2)
        self.avFFLabel.setObjectName("avFFLabel")
        self.gridLayout_2.addWidget(self.avFFLabel, 2, 0, 1, 1)
        self.avVocText = QLineEdit(self.gridLayoutWidget_2)
        self.avVocText.setObjectName("avVocText")
        self.gridLayout_2.addWidget(self.avVocText, 1, 1, 1, 1)
        self.corrVocText = QLineEdit(self.gridLayoutWidget_2)
        self.corrVocText.setObjectName("corrVocText")
        self.gridLayout_2.addWidget(self.corrVocText, 1, 3, 1, 1)
        self.avFFText = QLineEdit(self.gridLayoutWidget_2)
        self.avFFText.setObjectName("avFFText")
        self.gridLayout_2.addWidget(self.avFFText, 2, 1, 1, 1)
        self.corrFFText = QLineEdit(self.gridLayoutWidget_2)
        self.corrFFText.setObjectName("corrFFText")
        self.gridLayout_2.addWidget(self.corrFFText, 2, 3, 1, 1)
        
        self.deviceIDLabel.setText("Current Device ID")
        self.corrVocLabel.setText("Corresponding Voc [V]")
        self.corrJscLabel.setText("Corresponding Jsc [mA/cm^2]")
        self.corrFFLabel.setText("Corresponding FF")
        self.avVocLabel.setText("Average Voc [V]")
        self.avJscLabel.setText("Average Jsc [mA/cm^2]")
        self.avFFLabel.setText("Average FF")
        '''
        
        self.resTableWidget = QTableWidget(self.centralwidget)
        self.resTableWidget.setGeometry(QRect(10, 150, 500, 145))
        self.resTableWidget.setColumnCount(5)
        self.resTableWidget.setRowCount(4)
        self.resTableWidget.setItem(0,0, QTableWidgetItem(""))
        self.resTableWidget.setHorizontalHeaderItem(0,QTableWidgetItem("Device ID"))
        self.resTableWidget.setHorizontalHeaderItem(1,QTableWidgetItem("Av Voc [V]"))
        self.resTableWidget.setHorizontalHeaderItem(2,QTableWidgetItem("Av Jsc [mA/cm^2]"))
        self.resTableWidget.setHorizontalHeaderItem(3,QTableWidgetItem("Av FF"))
        self.resTableWidget.setHorizontalHeaderItem(4,QTableWidgetItem("Time"))

        self.resTableWidget.itemClicked.connect(self.onCellClick)

        self.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(self)
        self.menubar.setGeometry(QRect(0, 0, 1447, 22))
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)
        
        # Just some button connected to `plot` method
        self.randomButton = QPushButton(self.centralwidget)
        self.randomButton.setGeometry(QRect(500, 10, 200, 30))
        self.openButton = QPushButton(self.centralwidget)
        self.openButton.setGeometry(QRect(700, 10, 200, 30))
        self.clearButton = QPushButton(self.centralwidget)
        self.clearButton.setGeometry(QRect(900, 10, 200, 30))

        self.randomButton.setText("Plot Random Data")
        self.openButton.setText("Open Data")
        self.clearButton.setText("Clear Data")
        self.randomButton.clicked.connect(self.temporaryAcquisition)
        self.openButton.clicked.connect(self.open_data)
        self.clearButton.clicked.connect(self.clearPlots)
    
    
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
        self.summaryData = np.zeros((0,5))
        self.initPlots(self.summaryData)
        self.initJVPlot()
        '''
        self.corrVocText.setText("")
        self.corrJscText.setText("")
        self.corrFFText.setText("")
        self.avVocText.setText("")
        self.avJscText.setText("")
        self.avFFText.setText("")
        '''
        self.time = 0   #### This will be removed once testing of random plotting is done
    
    # Action upon selecting a row in the table.
    @pyqtSlot()
    def onCellClick(self):
        
        for j in range(self.resTableWidget.columnCount()):
            for i in range(self.resTableWidget.rowCount()):
                self.resTableWidget.setItem(i,j,QTableWidgetItem())
                self.resTableWidget.item(i,j).setBackground(QColor(255,255,255))

        for j in range(self.resTableWidget.columnCount()):
            row = self.resTableWidget.selectedItems()[0].row()
            self.resTableWidget.setItem(row,j,QTableWidgetItem())
            self.resTableWidget.item(row,j).setBackground(QColor(0,255,0))

        #for currentQTableWidgetItem in self.resTableWidget.selectedItems():
        #    print("Selected cell: ",currentQTableWidgetItem.row())
    
    ###### Processing #############
    def processData(self, time, JV):
        self.plotJVresp(JV)
        #QApplication.processEvents()

        currentData = self.analyseJV(JV)
        '''
        self.corrVocText.setText("{0:0.3f}".format(currentData[0]))
        self.corrJscText.setText("{0:0.3e}".format(currentData[1]))
        self.corrFFText.setText("{0:0.1f}".format(currentData[2]))
        '''
        
        self.summaryData = np.vstack((self.summaryData,np.hstack((time, currentData))))
        
        self.plotTVoc(self.summaryData)
        self.plotMPP(self.summaryData)
        self.plotTJsc(self.summaryData)
        QApplication.processEvents()
        '''
        self.avVocText.setText("{0:0.3f}".format(np.mean(self.summaryData[:,1])))
        self.avJscText.setText("{0:0.3e}".format(np.mean(self.summaryData[:,2])))
        self.avFFText.setText("{0:0.1f}".format(np.mean(self.summaryData[:,3])))
        '''
        self.show()
    
    def analyseJV(self, JV):
        PV = np.zeros(JV.shape)
        PV[:,0] = JV[:,0]
        PV[:,1] = JV[:,0]*JV[:,1]
        Voc = JV[JV.shape[0]-1,0]
        Jsc = JV[0,1]
        Vpmax = PV[np.where(PV == np.amax(PV)),0][0][0]
        Jpmax = JV[np.where(PV == np.amax(PV)),1][1][0]
        FF = Vpmax*Jpmax*100/(Voc*Jsc)
        data = np.array([Voc, Jsc, FF,Vpmax*Jpmax])
        return data
    
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
    
    ################################################################
    def generateRandomJV(self):
        VStart = 0
        VEnd = 1
        VStep = 0.02
        I0 = 1e-10
        Il = 0.5
        n = 1+ random.randrange(0,20,1)/10
        T = 300
        kB = 1.38064852e-23  # Boltzman constant m^2 kg s^-2 K^-1
        q = 1.60217662E-19  # Electron charge
        
        JV = np.zeros((0,2))
        for i in np.arange(VStart,VEnd,VStep):
            temp = Il - I0*math.exp(q*i/(n*kB*T))
            JV = np.vstack([JV,[i,temp]])
        JV[:,1] = JV[:,1]-np.amin(JV[:,1])
        return JV

    ### This will only be used for testing, to sumulate an actual experiment
    def temporaryAcquisition(self):
        self.time = self.time + 1
        self.processData(self.time, self.generateRandomJV())
