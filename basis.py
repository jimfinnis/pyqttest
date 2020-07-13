from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QPixmap,QImage

import cv2 as cv
import numpy as np

import sys

# make damn sure you do inherit from the root class of the UI
# here.

class Ui(QtWidgets.QMainWindow):

    # this safely gets a widget reference
    def getUI(self,type,name):
        x = self.findChild(type,name)
        if x is None:
            raise Exception('cannot find widget'+name)
        return x
        
    # grab an image, return a pixmap which we can then load
    # into a pixmapitem
    def capture(self):
        rv,img = self.cam.read()
        if rv == 0:
            raise Exception('cannot read image')
        else:
            # cv is bgr, qt (and sensible things) are rgb
            img = cv.cvtColor(img, cv.COLOR_BGR2RGB)

            # let's play with the image!
            img = tweak(img)

            height, width, channel = img.shape
            bytesPerLine = 3 * width
            qimg = QImage(img.data, width, height, 
                bytesPerLine, QImage.Format_RGB888)
            return QPixmap.fromImage(qimg)
    
    # capture button clicked
    def captureButtonAction(self):
        self.pixmapitem.setPixmap(self.capture())
        print("BANG")
        
    # confirm a quit menu action
    def confirmQuitAction(self):
        reply = QMessageBox.question(self, 
            'Confirm',
            'Really quit?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            app.quit()
        
    def __init__(self):
        super(Ui, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('test.ui', self) # Load the .ui file
        
        # now we get references to the widgets we want and connect
        # things up. Brackets here to make the line break work.
        (self.getUI(QtWidgets.QPushButton,'captureButton').
            clicked.connect(self.captureButtonAction))
        (self.getUI(QtWidgets.QAction,'actionQuit').
            triggered.connect(self.confirmQuitAction))
        
        # create a scene and set it into the view
        self.scene = QtWidgets.QGraphicsScene()
        self.getUI(QtWidgets.QGraphicsView,'graphicsView').setScene(self.scene)
        # create a pixmap item and add it to the scene.
        self.pixmapitem = QtWidgets.QGraphicsPixmapItem()
        self.scene.addItem(self.pixmapitem)
        
        # set up cv capture
        self.cam = cv.VideoCapture(0)
        self.cam.set(cv.CAP_PROP_FRAME_WIDTH,640);
        self.cam.set(cv.CAP_PROP_FRAME_HEIGHT,480);
        self.show() # Show the GUI
        
def tweak(img):
    # example tweak. Split img into channels, each is a numpy array
    # (as is the image, but the image is WxHx3).
    r,g,b = cv.split(img)
    # clip the red channel to a given range
    r = r.clip(100,200)
    # recombine channels
    return cv.merge((r,g,b))


# Create an instance of QtWidgets.QApplication
app = QtWidgets.QApplication(sys.argv) 
window = Ui() # Create an instance of our class
app.exec_() # Start the application
