#! /usr/bin/env python3
import sys
from PyQt4.QtGui import QApplication
import gridedgeat

try:
    app = QApplication(sys.argv)
    form = gridedgeat.gui.MainWindow()
    form.show()
    app.exec_()
finally:
    print("App is closing!")

