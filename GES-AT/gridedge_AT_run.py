#! /usr/bin/env python3
import sys
#from PyQt4.QtGui import QApplication
from PyQt5.QtWidgets import QApplication
import gridedgeat

try:
    app = QApplication(sys.argv)
    form = gridedgeat.mainWindow.MainWindow()
    form.show()
    app.exec_()
finally:
    print("App is closing!")

