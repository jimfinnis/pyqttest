from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QPixmap

import cv2 as cv

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
    
    # capture button clicked
    def capture(self):
        print("BANG")
        rv,img = self.cam.read()
        if rv == 0:
            print("cannot read")
        else:
            height, width, channel = img.shape
            bytesPerLine = 3 * width
            qimg = QImage(img.data, width, height, 
                bytesPerLine, QImage.Format_RGB888)
            self.pix.convertFromImage(img)
        
    # confirm a quit menu action
    def confirmQuit(self):
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
            clicked.connect(self.capture))
        (self.getUI(QtWidgets.QAction,'actionQuit').
            triggered.connect(self.confirmQuit))
        
        # create a scene and set it into the view
        self.scene = QtWidgets.QGraphicsScene()
        self.getUI(QtWidgets.QGraphicsView,'graphicsView').setScene(self.scene)
        # create a pixmap and add it to the scene.
        self.pix = QPixmap()
        self.scene.addPixmap(self.pix)
        
        # set up cv capture
        self.cam = cv.VideoCapture(0)

        self.show() # Show the GUI

# Create an instance of QtWidgets.QApplication
app = QtWidgets.QApplication(sys.argv) 
window = Ui() # Create an instance of our class
app.exec_() # Start the application
