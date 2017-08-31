'''
switchboxWindow
------------------
Class for providing a graphical user interface for 
switchbox

Copyright (C) 2017 Nicola Ferralis <ferralis@mit.edu>
Copyright (C) 2017 Auto-testing team - MIT GridEdge Solar

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

'''

from PyQt5.QtCore import QRect
from PyQt5.QtWidgets import (QLabel, QLineEdit, QCheckBox, QWidget,QMainWindow)
#from .modules.switchbox.switchbox import *

class SwitchboxWindow(QMainWindow):
    def __init__(self, parent=None):
        super(SwitchboxWindow, self).__init__(parent)
        self.initUI(self)
    
    def initUI(self, SwitchboxWindow):
        SwitchboxWindow.resize(328, 60)
        self.stageLabel = QLabel(SwitchboxWindow)
        self.stageLabel.setGeometry(QRect(20, 20, 300, 16))
        SwitchboxWindow.setWindowTitle("Switchbox controls")
        self.stageLabel.setText("Functionality not yet implemented")
