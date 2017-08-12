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
from datetime import datetime
from .qt.widgets import (QMainWindow, QApplication, QPushButton, QWidget, QAction,
    QVBoxLayout,QGridLayout,QLabel,QGraphicsView,QKeySequence,QFileDialog,QStatusBar,
    QPixmap,QGraphicsScene,QPainter,QLineEdit,QMessageBox,QDialog,QPushButton)
from .qt.QtGui import (QIcon,QImage)
from .qt.QtCore import (pyqtSlot,QRectF)
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
        self.setGeometry(500, 100, 400, 400)
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
        self.button = QPushButton('Plot')
        self.button.clicked.connect(self.plot)

        # set the layout
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        layout.addWidget(self.button)
        self.setLayout(layout)
        
    def plot(self):
        ''' plot some random stuff '''
        # random data
        data = [random.random() for i in range(10)]

        # create an axis
        ax = self.figure.add_subplot(111)

        # discards the old graph
        ax.clear()

        # plot data
        ax.plot(data, '*-')

        # refresh canvas
        self.canvas.draw()
