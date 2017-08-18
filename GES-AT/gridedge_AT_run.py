#! /usr/bin/env python3
'''
GridEdge Autotesting runtime
------------------
Launcher for the GridEdge Autotesting Software

Copyright (C) 2017 Nicola Ferralis <ferralis@mit.edu>
Copyright (C) 2017 Auto-testing team - MIT GridEdge Solar

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

'''
import sys
from PyQt5.QtWidgets import QApplication
import gridedgeat

try:
    app = QApplication(sys.argv)
    form = gridedgeat.mainWindow.MainWindow()
    form.show()
    app.exec_()
finally:
    print("App is closing!")

