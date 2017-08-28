import sys
from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor

class Window(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.figure = plt.figure(facecolor='white')
        self.canvas = FigureCanvas(self.figure)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        ''' plot some random stuff '''
        ax = self.figure.add_subplot(111)
        self.ax = ax
        ax.plot([1,2])
        # Set cursor        
        cursor = Cursor(self.ax, useblit=False, color='red', linewidth=1)

        ############## The added part: #############
        def onclick(event):
            cursor.onmove(event)
        self.canvas.mpl_connect('button_press_event', onclick)
        ############################################
        self.canvas.draw()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = Window()
    main.show()
    sys.exit(app.exec_())
