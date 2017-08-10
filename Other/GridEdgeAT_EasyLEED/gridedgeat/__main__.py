#! /usr/bin/env python3

import sys
from .qt.widgets import QApplication
from .gui import MainWindow

def main():
    app = QApplication(sys.argv)
    form = MainWindow()
    app.exec_()

if __name__ == "__main__":
    main()
