#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PIL import Image
from PIL.ImageQt import ImageQt

import time

class TestWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.button = QPushButton("Do test")

        layout = QVBoxLayout()
        layout.addWidget(self.button)
        layout.addWidget(self.view)
        self.setLayout(layout)

        self.button.clicked.connect(self.do_test)

    def do_test(self):
        img = Image.open('image.png')
        self.display_image(img)
        QCoreApplication.processEvents()  # let Qt do his work
        time.sleep(0.5)

    def display_image(self, img):
        self.scene.clear()
        w, h = img.size
        self.imgQ = ImageQt(img)  # we need to hold reference to imgQ, or it will crash
        pixMap = QPixmap.fromImage(self.imgQ)
        self.scene.addPixmap(pixMap)
        self.view.fitInView(QRectF(0, 0, w, h), Qt.KeepAspectRatio)
        self.scene.update()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = TestWidget()
    widget.resize(640, 480)
    widget.show()

    sys.exit(app.exec_())

