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
from PyQt5.QtWidgets import (QMainWindow,QPushButton,QVBoxLayout,QFileDialog,QWidget,
            QGridLayout,QGraphicsView,QLabel,QComboBox,QLineEdit,QMenuBar,QStatusBar)
from PyQt5.QtCore import (QRect)
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
        self.initPlots()
        self.initJVPlot()
        self.summaryData = np.zeros((0,5))
        self.time = 0

    
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
        self.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(self)
        self.menubar.setGeometry(QRect(0, 0, 1447, 22))
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)
        
        self.deviceIDLabel.setText("Current Device ID")
        self.corrVocLabel.setText("Corresponding Voc [V]")
        self.corrJscLabel.setText("Corresponding Jsc [mA/cm^2]")
        self.corrFFLabel.setText("Corresponding FF")
        self.avVocLabel.setText("Average Voc [V]")
        self.avJscLabel.setText("Average Jsc [mA/cm^2]")
        self.avFFLabel.setText("Average FF")
        
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
    
    def initPlots(self):
        self.figureTJsc.clf()
        self.axTJsc = self.figureTJsc.add_subplot(111)
        self.plotSettings(self.axTJsc)
        self.axTJsc.set_xlabel('Time [s]',fontsize=5)
        self.axTJsc.set_ylabel('Jsc [mA/cm^2]',fontsize=5)
        self.canvasTJsc.draw()
        self.figureTVoc.clf()
        self.axTVoc = self.figureTVoc.add_subplot(111)
        self.plotSettings(self.axTVoc)
        self.axTVoc.set_xlabel('Time [s]',fontsize=5)
        self.axTVoc.set_ylabel('Voc [V]',fontsize=5)
        self.canvasTVoc.draw()
        self.figureMPP.clf()
        self.axMPP = self.figureMPP.add_subplot(111)
        self.plotSettings(self.axMPP)
        self.axMPP.set_xlabel('Time [s]',fontsize=5)
        self.axMPP.set_ylabel('Max power point [mW]',fontsize=5)
        self.canvasMPP.draw()
    
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
        self.axTJsc.plot(data[:,0],data[:,2], '.-',linewidth=0.5)
        self.canvasTJsc.draw()
    
    # Plot Transient Voc
    def plotTVoc(self, data):
        self.axTVoc.plot(data[:,0],data[:,1], '.-',linewidth=0.5)
        self.canvasTVoc.draw()

    # Plot MPP with tracking
    def plotMPP(self, data):
        self.axMPP.plot(data[:,0],data[:,4], '.-',linewidth=0.5)
        self.canvasMPP.draw()
    
    # Plot JV response
    def plotJVresp(self, JV):
        self.initJVPlot()
    
        self.axJVresp.plot(JV[:,0],JV[:,1], '.-',linewidth=0.5)
        self.axPVresp.plot(JV[:,0],JV[:,0]*JV[:,1], '.-',linewidth=0.5,
                color='orange')
        self.canvasJVresp.draw()
    
    def clearPlots(self):
        self.initPlots()
        self.initJVPlot()
        self.corrVocText.setText("")
        self.corrJscText.setText("")
        self.corrFFText.setText("")
        self.avVocText.setText("")
        self.avJscText.setText("")
        self.avFFText.setText("")
        self.time = 0
        self.summaryData = np.zeros((0,5))
    
    ###### Processing #############
    
    def temporaryAcquisition(self):
        self.time = self.time + 1
        self.processData(self.generateRandomJV())
    
    def processData(self,JV):
        self.plotJVresp(JV)
        currentData = self.analyseJV(JV)
        self.corrVocText.setText("{0:0.3f}".format(currentData[1]))
        self.corrJscText.setText("{0:0.3e}".format(currentData[2]))
        self.corrFFText.setText("{0:0.1f}".format(currentData[3]))
        
        self.summaryData = np.vstack((self.summaryData,np.hstack((self.time, currentData))))
        
        self.plotTVoc(self.summaryData)
        self.plotMPP(self.summaryData)
        self.plotTJsc(self.summaryData)


    def open_data(self):
        filenames = QFileDialog.getOpenFileNames(self,
                        "Open ASCII data", "","*.txt")
        try:
            for filename in filenames:
                data = open(filename)
                M = np.loadtxt(data,unpack=False)
                self.plotJVresp(M)
        except:
            print("Loading files failed")
    
    def analyseJV(self,JV):
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

    ### deprecated ####
    def generate_random_data(self):
        self.data = np.empty((10,2))
        self.data[:,0] = [i for i in range(10)]
        #self.data[:,1] = [random.random() for i in range(10)]
        #self.plotJVresp(self.data)
        self.data[:,1] = [random.random() for i in range(10)]
        self.plotTVoc(self.data)
        self.data[:,1] = [random.random() for i in range(10)]
        self.plotTJsc(self.data)
        self.data[:,1] = [random.random() for i in range(10)]
        self.plotMPP(self.data)
        self.JV = self.generateRandomJV()
        self.plotJVresp(self.JV)

