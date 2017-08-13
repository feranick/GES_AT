'''
plotWindow.py
-------------
Classes for providing a graphical user interface
for the plotWindow

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
from .qt.widgets import (QPushButton,QVBoxLayout,QFileDialog,QDialog)
from .qt import qt_filedialog_convert
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

from . import config


'''
   Plot Window
'''
class PlotWindow(QDialog):
    def __init__(self):
        super(PlotWindow, self).__init__()
        self.initUI()
    
    def initUI(self):
        self.setGeometry(500, 100, 600, 600)
        self.setWindowTitle('Plot Panel')
        #self.statusBar().showMessage("Plotting: Ready", 5000)
        # a figure instance to plot on
        self.figure = plt.figure()

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)

        # Just some button connected to `plot` method
        self.randomBtn = QPushButton('Plot random data')
        self.randomBtn.clicked.connect(self.generate_random_data)
        self.openBtn = QPushButton('Open data')
        self.openBtn.clicked.connect(self.open_data)

        # set the layout
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        layout.addWidget(self.randomBtn)
        layout.addWidget(self.openBtn)
        self.setLayout(layout)

    def generate_random_data(self):
        self.data = np.empty((10,2))
        self.data[:,0] = [i for i in range(10)]
        self.data[:,1] = [random.random() for i in range(10)]

        self.plot(self.data)

    def plot(self, data):
        ''' plot some random stuff '''
        ax = self.figure.add_subplot(111)
        ax.clear()
        ax.plot(data[:,0],data[:,1], '*-')
        ax.set_xlabel('Voltage [V]')
        ax.set_ylabel('Current density [mA/cm^2]')
        self.canvas.draw()

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
