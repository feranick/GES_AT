from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys, time

#First we create a QApplication and QPushButton
app=QApplication(sys.argv)
exitButton=QPushButton("Exit")

#Here we connect the exitButton's "clicked()" signals to the app's exit method. 
#This will have the effect that every time some one clicks the exitButton 
#the app.exit method will execute and the application will close.
#QObject.connect(exitButton,SIGNAL("clicked()"),app.exit)

while True:

    exitButton.clicked.connect(app.exit)
    
    exitButton.show()




#Start the evnt loop
sys.exit(app.exec_())
