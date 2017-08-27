import sys
from PyQt5 import QtGui, QtCore, QtWidgets


class Communicate(QtCore.QObject):
    
    closeApp = QtCore.pyqtSignal() 
    

class Example(QtWidgets.QMainWindow):
    
    def __init__(self):
        super(Example, self).__init__()
        
        self.initUI()
        
        
    def initUI(self):      

        self.c = Communicate()
        self.c.closeApp.connect(self.close)       
        
        self.setGeometry(300, 300, 290, 150)
        self.setWindowTitle('Emit signal')
        self.show()
        
        
    def mousePressEvent(self, event):
        quit_msg = "Are you sure you want to exit the program?"
        reply = QtWidgets.QMessageBox.question(self, 'Message',
                     quit_msg, QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            self.c.closeApp.emit()
        else:
            event.ignore()
        #self.c.closeApp.emit()

    def closeEvent(self, event):
        quit_msg = "Are you sure you want to exit the program?"
        reply = QtWidgets.QMessageBox.question(self, 'Message',
                     quit_msg, QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            self.close()
        else:
            event.ignore()
        
        
def main():
    
    app = QtWidgets.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
