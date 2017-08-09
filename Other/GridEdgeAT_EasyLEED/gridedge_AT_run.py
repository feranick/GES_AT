#! /usr/bin/env python3
import sys
from PyQt4.QtGui import QApplication
import gridedgeat

app = QApplication(sys.argv)
form = gridedgeat.gui.MainWindow()
form.show()
app.exec_()
