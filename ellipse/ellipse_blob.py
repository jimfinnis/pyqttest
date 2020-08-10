import cv2 as cv
import numpy as np
import math

from functools import reduce
import cluster

# histogram equalization
def equalize(input):
    img,data = input
    r,g,b = cv.split(img)
    r = cv.equalizeHist(r)
    g = cv.equalizeHist(g)
    b = cv.equalizeHist(b)
    img = cv.merge((r,g,b))
    return (img,None,False,"equalize")
    
def ellipseDetect(input):
    img,data = input
    params = cv.SimpleBlobDetector_Params()

    area = img.shape[0]*img.shape[1]
    
    minArea = area*0.000125
    maxArea = area*0.002
    print(area,minArea,maxArea)
      
    bestcount = 0
    
    # use varying maximum threshold, keep the largest number
    # of blobs found (if it's less than 8)
    
    for maxthresh in range(20,225,10):
        params.thresholdStep = 10.0
        params.minThreshold = 10
        params.maxThreshold = maxthresh #220.0
 
        params.filterByArea = True
        params.minArea = minArea
        params.maxArea = maxArea

        params.filterByColor = False

        params.filterByCircularity = True
        params.minCircularity = 0.7

        params.filterByConvexity = True
        params.minConvexity = 0.8
 
        params.filterByInertia = True
        params.minInertiaRatio = 0.5
 
        params.minRepeatability = 2
        params.minDistBetweenBlobs= 10.0

        detector = cv.SimpleBlobDetector_create(params)
        keypoints = detector.detect(img)
        
        keypoints = cluster.cluster(keypoints,5)
        if keypoints is not None:
            count = len(keypoints)
            for p in keypoints:
                print(p.pt,p.size)
            if count<=8 and count>bestcount:
                bestcount=count
                bestpoints=keypoints
        
    if bestcount>0:
        keypoints=bestpoints        
        print(keypoints)
        img = cv.drawKeypoints(img, keypoints, 
                None, (255, 0, 0), 
                cv.DrawMatchesFlags_DRAW_RICH_KEYPOINTS )
    else:
        keypoints=list()
        print("No ellipses found")
    return(img,keypoints,True,("blob ellipses","%d keypoints" % bestcount))

# each stage goes in here, they are all functions which take an
# (image,data) tuple and return an (image,data,boolean,text/tuple) tuple. 
# Images are numpy/cv, and are either (x,y) or (x,y,3) ubyte arrays --- 8 bit and
# 24 bit colour respectively.
# The data field is used to pass non-image info between stages (and is
# the output in the last stage), and the boolean field is true
# for the last stage. Text is displayed in the image. If it's a tuple,
# the first element is output to the image, the second to the status

stages= [ ellipseDetect ]

# run stage n: each stage takes and returns an image

def stage(n,input):
    if n<len(stages):
        return stages[n](input)
    else:
        img,data = input
        return (img,data,True,'done')
    

