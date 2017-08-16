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

import sys, random
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
    
    def initUI(self):
        self.setGeometry(500, 100, 1150, 925)
        self.setWindowTitle('Results Panel')
        
        # a figure instance to plot on
        self.figureTJsc = plt.figure()
        self.figureTVoc = plt.figure()
        self.figureJVresp = plt.figure()
        self.figureMPP = plt.figure()
        
        self.centralwidget = QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayoutWidget = QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QRect(20, 40, 1100, 710))
        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.canvasTVoc = FigureCanvas(self.figureTVoc)
        self.gridLayout.addWidget(self.canvasTVoc, 1, 1, 1, 1)
        self.canvasMPP = FigureCanvas(self.figureMPP)
        self.gridLayout.addWidget(self.canvasMPP, 3, 1, 1, 1)
        self.canvasJVresp = FigureCanvas(self.figureJVresp)
        self.gridLayout.addWidget(self.canvasJVresp, 1, 0, 1, 1)
        self.canvasTJsc = FigureCanvas(self.figureTJsc)
        self.gridLayout.addWidget(self.canvasTJsc, 3, 0, 1, 1)
        
        self.toolbarTJsc = NavigationToolbar(self.canvasTJsc, self)
        self.gridLayout.addWidget(self.toolbarTJsc, 0, 0, 1, 1)
        self.toolbarTVoc = NavigationToolbar(self.canvasTVoc, self)
        self.gridLayout.addWidget(self.toolbarTVoc, 2, 0, 1, 1)
        self.toolbarJVresp = NavigationToolbar(self.canvasJVresp, self)
        self.gridLayout.addWidget(self.toolbarJVresp, 0, 1, 1, 1)
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
        self.CorrVocLabel = QLabel(self.gridLayoutWidget_2)
        self.CorrVocLabel.setObjectName("CorrVocLabel")
        self.gridLayout_2.addWidget(self.CorrVocLabel, 1, 2, 1, 1)
        self.corrJscLabel = QLabel(self.gridLayoutWidget_2)
        self.corrJscLabel.setObjectName("corrJscLabel")
        self.gridLayout_2.addWidget(self.corrJscLabel, 0, 2, 1, 1)
        self.CorrFFLabel = QLabel(self.gridLayoutWidget_2)
        self.CorrFFLabel.setObjectName("CorrFFLabel")
        self.gridLayout_2.addWidget(self.CorrFFLabel, 2, 2, 1, 1)
        self.AvVocLabel = QLabel(self.gridLayoutWidget_2)
        self.AvVocLabel.setObjectName("AvVocLabel")
        self.gridLayout_2.addWidget(self.AvVocLabel, 1, 0, 1, 1)
        self.AvFFLabel = QLabel(self.gridLayoutWidget_2)
        self.AvFFLabel.setObjectName("AvFFLabel")
        self.gridLayout_2.addWidget(self.AvFFLabel, 2, 0, 1, 1)
        self.AvVocText = QLineEdit(self.gridLayoutWidget_2)
        self.AvVocText.setObjectName("AvVocText")
        self.gridLayout_2.addWidget(self.AvVocText, 1, 1, 1, 1)
        self.CorrVocText = QLineEdit(self.gridLayoutWidget_2)
        self.CorrVocText.setObjectName("CorrVocText")
        self.gridLayout_2.addWidget(self.CorrVocText, 1, 3, 1, 1)
        self.AvFFText = QLineEdit(self.gridLayoutWidget_2)
        self.AvFFText.setObjectName("AvFFText")
        self.gridLayout_2.addWidget(self.AvFFText, 2, 1, 1, 1)
        self.CorrFFText = QLineEdit(self.gridLayoutWidget_2)
        self.CorrFFText.setObjectName("CorrFFText")
        self.gridLayout_2.addWidget(self.CorrFFText, 2, 3, 1, 1)
        self.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(self)
        self.menubar.setGeometry(QRect(0, 0, 1447, 22))
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)
        
        self.deviceIDLabel.setText("Current Device ID")
        self.avJscLabel.setText("Average Jsc")
        self.CorrVocLabel.setText("Corresponding Voc")
        self.corrJscLabel.setText("Corresponding Jsc")
        self.CorrFFLabel.setText("Corresponding FF")
        self.AvVocLabel.setText("Average Voc")
        self.AvFFLabel.setText("Average FF")
        
        # Just some button connected to `plot` method
        self.randomButton = QPushButton(self.centralwidget)
        self.randomButton.setGeometry(QRect(500, 10, 200, 30))
        self.openButton = QPushButton(self.centralwidget)
        self.openButton.setGeometry(QRect(700, 10, 200, 30))
        self.openButton.setObjectName("openButton")
        
        self.randomButton.setText("Plot Random Data")
        self.openButton.setText("Open Data")
        self.randomButton.clicked.connect(self.generate_random_data)
        self.openButton.clicked.connect(self.open_data)
    
    def plotSettings(self, ax):
        ax.tick_params(axis='both', which='major', labelsize=5)
        ax.tick_params(axis='both', which='minor', labelsize=5)

    # Plot Transient Jsc
    def plotTJsc(self, data):
        ax = self.figureTJsc.add_subplot(111)
        ax.clear()
        self.plotSettings(ax)
        ax.plot(data[:,0],data[:,1], '*-')
        ax.set_xlabel('Time [s]',fontsize=5)
        ax.set_ylabel('Jsc [mA/cm^2]',fontsize=5)
        self.canvasTJsc.draw()
    
    # Plot Transient Voc
    def plotTVoc(self, data):
        ax = self.figureTVoc.add_subplot(111)
        ax.clear()
        self.plotSettings(ax)
        ax.plot(data[:,0],data[:,1], '*-')
        ax.set_xlabel('Time [s]',fontsize=5)
        ax.set_ylabel('Voc [V]',fontsize=5)
        self.canvasTVoc.draw()
    
    # Plot JV response
    def plotJVresp(self, data):
        ax = self.figureJVresp.add_subplot(111)
        ax.clear()
        self.plotSettings(ax)
        ax.tick_params(axis='both', which='major', labelsize=5)
        ax.tick_params(axis='both', which='minor', labelsize=5)
        ax.plot(data[:,0],data[:,1], '*-')
        ax.set_xlabel('Voltage [V]',fontsize=5)
        ax.set_ylabel('Current density [mA/cm^2]',fontsize=5)
        self.canvasJVresp.draw()
    
    # Plot MPP with tracking
    def plotMPP(self, data):
        ax = self.figureMPP.add_subplot(111)
        ax.clear()
        self.plotSettings(ax)
        ax.tick_params(axis='both', which='major', labelsize=5)
        ax.tick_params(axis='both', which='minor', labelsize=5)
        ax.plot(data[:,0],data[:,1], '*-')
        ax.set_xlabel('Time [s]',fontsize=5)
        ax.set_ylabel('Max Power Point [mW]',fontsize=5)
        self.canvasMPP.draw()

    def open_data(self):
        filenames = QFileDialog.getOpenFileNames(self,
                        "Open ASCII data", "","*.txt")
        try:
            for filename in filenames:
                data = open(filename)
                M = np.loadtxt(data,unpack=False)
                self.plot(M)
        except:
            print("Loading files failed")

    def generate_random_data(self):
        self.data = np.empty((10,2))
        self.data[:,0] = [i for i in range(10)]
        self.data[:,1] = [random.random() for i in range(10)]
        self.plotTJsc(self.data)
        self.data[:,1] = [random.random() for i in range(10)]
        self.plotTVoc(self.data)
        self.data[:,1] = [random.random() for i in range(10)]
        self.plotJVresp(self.data)
        self.data[:,1] = [random.random() for i in range(10)]
        self.plotMPP(self.data)
