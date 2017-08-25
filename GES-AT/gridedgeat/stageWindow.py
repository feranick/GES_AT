'''
stageWindow
------------------
Class for providing a graphical user interface for 
XY stage panel

Copyright (C) 2017 Nicola Ferralis <ferralis@mit.edu>
Copyright (C) 2017 Auto-testing team - MIT GridEdge Solar

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

'''

from PyQt5.QtCore import QRect
from PyQt5.QtWidgets import (QLabel, QLineEdit, QCheckBox, QWidget)
from .modules.powermeter import *

class StageWindow(QWidget):

    def __init__(self, parent=None):
        super(StageWindow, self).__init__(parent)
        self.initUI(self)
    
    def initUI(self, StageWindow):
        StageWindow.resize(328, 60)
        self.stageLabel = QLabel(StageWindow)
        self.stageLabel.setGeometry(QRect(20, 20, 300, 16))
        StageWindow.setWindowTitle("XY Stage")
        self.stageLabel.setText("Functionality not yet implemented")
