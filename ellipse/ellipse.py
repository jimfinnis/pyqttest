import cv2 as cv
import numpy as np

from skimage.feature import canny
from skimage.transform import hough_ellipse
from skimage.draw import ellipse_perimeter


def edgeDetect(input):
    img,_ = input
    # greyscale
    img = 0.299*img[:,:,0]+0.587*img[:,:,1]+0.114*img[:,:,2]
    print(img.shape)
    
    return (canny(img,sigma=1,low_threshold=20,high_threshold=50),None)
    
def ellipseDetect(input):
    edges,_ = input
    result = hough_ellipse(edges,accuracy=1,threshold=2,min_size=5,max_size=20)
    result.sort(order='accumulator')
    result = [x for x in result if x[4]>2 and x[3]>2] # must be non-degenerate
    result = [x for x in result if abs(x[4]/x[3]-1.0)<0.2] # nearly circular
    best = result[-100:]
    
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
    return (img,best)

# each stage goes in here, they are all functions which take and return an (image,data) tuple
# Images are numpy/cv, and are either (x,y) or (x,y,3) ubyte arrays --- 8 bit and
# 24 bit colour respectively.

stages= [ edgeDetect,ellipseDetect ]

# run stage n: each stage takes and returns an image

def stage(n,img):
    if n<len(stages):
        return stages[n](img)        
    else:
        return img
    
