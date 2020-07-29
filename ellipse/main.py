from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox,QFileDialog
from PyQt5.QtGui import QPixmap,QImage

import cv2 as cv
import numpy as np
import time
from skimage.feature import canny
from skimage.transform import hough_ellipse
from skimage.draw import ellipse_perimeter

import sys

# make damn sure you do inherit from the root class of the UI
# here. This is the top level class in the .ui XML file.

class Ui(QtWidgets.QMainWindow):

    # this safely gets a widget reference
    def getUI(self,type,name):
        x = self.findChild(type,name)
        if x is None:
            raise Exception('cannot find widget'+name)
        return x
        
    def cropSquare(self,img,x,y,size):
        return img[y:y+size,x:x+size]
    def loadFile(self,fname):
        img = cv.imread(fname)
        print("Image read")
        if img is None:
            raise Exception('cannot read image')
        else:
            # first, crop (note - indices are (y,x)) and resize
            img = self.cropSquare(img,340,430,100)
#            img = cv.resize(img,dsize=(100,100), interpolation=cv.INTER_CUBIC)
 
            # cv is bgr, qt (and sensible things) are rgb
            # convert to grayscale, favouring the green. You
            # could do this with img = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
            # but I'm demonstrating stuff here.
            img = 0.299*img[:,:,0]+0.587*img[:,:,1]+0.114*img[:,:,2]
            # once we've done that we have a float array which needs
            # to be converted to ubytes again.
            img = img.astype(np.ubyte)
            self.setImage(img)
    
        
    def openFileAction(self):
        fname,_ = QFileDialog.getOpenFileName(self, 'Open file', 
           '.',"Image files (*.jpg *.gif)")
        if fname is None or fname == '':
            return
        self.loadFile(fname)
        
    def findEllipsesAction(self):
        # generates a boolean array
        print(self.currentImage)
        edges = canny(self.currentImage,sigma=1,low_threshold=20,high_threshold=50)
        img = edges.astype(np.ubyte)*255
        
#        return
        
        print("Starting ellipse scan")
        start = time.perf_counter()
        result = hough_ellipse(edges,accuracy=1,threshold=2,min_size=5,max_size=20)
        print(time.perf_counter()-start)
        result.sort(order='accumulator')
        result = [x for x in result if x[4]>2 and x[3]>2] # must be non-degenerate
        result = [x for x in result if abs(x[4]/x[3]-1.0)<0.2] # nearly circular
        best = result[-100:]

        # get grayscale
        img = edges.astype(np.ubyte)*255
        # merge together into a 3 channel grayscale
        img = cv.merge([img,img,img])
        # show results
        for e in best:
            ee = list(e)
            yc, xc, a, b = [int(round(x)) for x in ee[1:5]]
            orientation = ee[5]
        

            # draw ellipse
            cy, cx = ellipse_perimeter(yc, xc, a, b, orientation)
            cx = np.clip(cx,0,99)
            cy = np.clip(cy,0,99)
            img[cy, cx] = (255, 0, 0)
            

        img = cv.resize(img,dsize=(300,300), interpolation=cv.INTER_CUBIC)

        # now convert to a QImage for display.
        height, width, channel = img.shape
        bytesPerLine = 3 * width
        qimg = QImage(img.data, width, height, 
            bytesPerLine, QImage.Format_RGB888)
        # and convert that to a QPixmap.
        pm = QPixmap.fromImage(qimg)
        self.pixmapitem2.setPixmap(pm)


    # show a grayscale image and set it as the current image.
    def setImage(self,image):
        self.currentImage = image
        # merge together into a 3 channel grayscale
        img = cv.merge([image,image,image])
        img = cv.resize(img,dsize=(300,300), interpolation=cv.INTER_CUBIC)
        # now convert to a QImage for display.
        height, width, channel = img.shape
        bytesPerLine = 3 * width
        qimg = QImage(img.data, width, height, 
            bytesPerLine, QImage.Format_RGB888)
        # and convert that to a QPixmap.
        pm = QPixmap.fromImage(qimg)
        self.pixmapitem.setPixmap(pm)
                

    # confirm a quit menu action
    def confirmQuitAction(self):
#        reply = QMessageBox.question(self, 
#            'Confirm',
#            'Really quit?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
#        if reply == QMessageBox.Yes:
#            app.quit()
        app.quit()
        
    def __init__(self):
        super(Ui, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('test.ui', self) # Load the .ui file
        
        # now we get references to the widgets we want and connect
        # things up. Brackets here to make the line break work.
        (self.getUI(QtWidgets.QAction,'actionQuit').
            triggered.connect(self.confirmQuitAction))
        (self.getUI(QtWidgets.QAction,'actionOpen').
            triggered.connect(self.openFileAction))

        (self.getUI(QtWidgets.QPushButton,'findEllipsesButton').
            clicked.connect(self.findEllipsesAction))
        
        # create a scene and set it into the view
        scene = QtWidgets.QGraphicsScene()
        self.getUI(QtWidgets.QGraphicsView,'graphicsView').setScene(scene)
        # create a pixmap item and add it to the scene.
        self.pixmapitem = QtWidgets.QGraphicsPixmapItem()
        scene.addItem(self.pixmapitem)
        
        scene = QtWidgets.QGraphicsScene()
        self.getUI(QtWidgets.QGraphicsView,'graphicsView2').setScene(scene)
        # create a pixmap item and add it to the scene.
        self.pixmapitem2 = QtWidgets.QGraphicsPixmapItem()
        scene.addItem(self.pixmapitem2)
        
        
        self.show() # Show the GUI
        self.loadFile('thumbnail.png')
        
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
