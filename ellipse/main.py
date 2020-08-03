from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox,QFileDialog
from PyQt5.QtGui import QPixmap,QImage,QPainter
from PyQt5.QtCore import Qt
import cv2 as cv
import numpy as np
import time,sys,math

import ellipse

# sizes of "slots" showing the various stages of processing in the view
VIEWSLOTW = 300
VIEWSLOTH = 300

# input: numpy w x h x 3 image, RGB floats
# output: numpy w x h image, ubyte
def greyscale(img):
    # convert to grayscale, favouring the green.
    # could do this with img = cv.cvtColor(img,cv.COLOR_RGB2GRAY)
    img = 0.299*img[:,:,0]+0.587*img[:,:,1]+0.114*img[:,:,2]
    return img.astype(np.ubyte)

def color(img):
    # convert greyscale to color; is naturally not the inverse of the above
    return cv.merge([img,img,img])
 
# convert a cv/numpy image to a Qt image
# input must be 3 channel 8 bit
def img2qimage(img):
    height, width, channel = img.shape
    bytesPerLine = 3 * width
    return QImage(img.data, width, height, 
        bytesPerLine, QImage.Format_RGB888)
    
def cropSquare(img,x,y,size):
    return img[y:y+size,x:x+size]


class Canvas(QtWidgets.QWidget):
    def __init__(self,parent):
        super(QtWidgets.QWidget,self).__init__(parent)
        # set up 10 empty "slots" (not the same as qt slots) to draw into
        self.displaySlots = [None for x in range(0,10)]
        
    # set an image into a slot - handles 8-bit and 24-bit; also boolean arrays (i.e.
    # edges)
    def display(self,slot,img):
        if img.dtype=='bool':
            img = img.astype(np.ubyte)*255
        if len(img.shape)==2:
            img = color(img)
        self.displaySlots[slot]=img
        self.update()

    # show a 24-bit colour image in the pixmap, in a given slot -
    # done as part of update, data is set by displaySlot888
    def drawDisplaySlot888(self,painter,slot):
        x = (slot%3)*VIEWSLOTW
        y = math.floor(slot/3)*VIEWSLOTH
        img = self.displaySlots[slot]
        if img is not None:
            # resize to slot size
            img = cv.resize(img,dsize=(VIEWSLOTW,VIEWSLOTH),interpolation=cv.INTER_CUBIC)
            qimg = img2qimage(img)
            painter.drawImage(x,y,qimg)
        else:   
            painter.fillRect(x,y,VIEWSLOTW,VIEWSLOTH,Qt.blue)

    def paintEvent(self,event):
        p = QPainter(self)
        p.eraseRect(event.rect())
        for i in range(0,10):
            self.drawDisplaySlot888(p,i)
        p.end()

        
        
class Ui(QtWidgets.QMainWindow):

    # input: filename
    # output: numpy w x h x 3 image, RGB 0-255
    
    def loadFile(self,fname):
        img = cv.imread(fname)
        print("Image read")
        if img is None:
            raise Exception('cannot read image')
        # cv is bgr, qt (and sensible things) are rgb
        img = cv.cvtColor(img,cv.COLOR_BGR2RGB)

        # crop to ROI and resize to 100x100
        img = cropSquare(img,340,430,100)
        img = cv.resize(img,dsize=(100,100), interpolation=cv.INTER_CUBIC)
        # convert to greyscale
        self.img=greyscale(img)
        self.canvas.display(0,self.img)
        self.stage=0
    
    # open file, get ROI and convert to grey
    def openFileAction(self):
        fname,_ = QFileDialog.getOpenFileName(self, 'Open file', 
           '.',"Image files (*.jpg *.gif)")
        if fname is None or fname == '':
            return
        self.loadFile(fname)
        
    def findEllipsesAction(self):
        print("Stage {0}, image {1} ".format(self.stage,self.img.shape))
        start = time.perf_counter()
        self.img = ellipse.stage(self.stage,self.img)
        self.stage=self.stage+1
        self.canvas.display(self.stage,self.img)
        print("Time taken {0} ".format(time.perf_counter()-start))
        
        
    # confirm a quit menu action
    def confirmQuitAction(self):
#        reply = QMessageBox.question(self, 
#            'Confirm',
#            'Really quit?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
#        if reply == QMessageBox.Yes:
#            app.quit()
        app.quit()
        

    # this safely gets a widget reference
    def getUI(self,type,name):
        x = self.findChild(type,name)
        if x is None:
            raise Exception('cannot find widget '+name)
        return x
        
    def __init__(self,*args,**kwargs):
        super(Ui, self).__init__(*args,**kwargs) # Call the inherited classes __init__ method
        uic.loadUi('test.ui', self) # Load the .ui file
        
        # now we get references to the widgets we want and connect
        # things up. Brackets here to make the line break work.
        (self.getUI(QtWidgets.QAction,'actionQuit').
            triggered.connect(self.confirmQuitAction))
        (self.getUI(QtWidgets.QAction,'actionOpen').
            triggered.connect(self.openFileAction))

        (self.getUI(QtWidgets.QPushButton,'findEllipsesButton').
            clicked.connect(self.findEllipsesAction))
        
        self.canvas = self.getUI(QtWidgets.QWidget,'view')
        
        self.show() # Show the GUI
        self.loadFile('thumbnail.png')
        self.stage = 0

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv) 
    window = Ui() # Create an instance of our class
    app.exec_() # Start the application
