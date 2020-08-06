import cv2 as cv
import numpy as np
import math

def ellipseDetect(input):
    img,data = input
    params = cv.SimpleBlobDetector_Params()
      
    bestcount = 0
    
    # use varying maximum threshold, keep the largest number
    # of blobs found (if it's less than 8)
    
    for maxthresh in range(0,255,5):
        params.thresholdStep = 10.0
        params.minThreshold = 10
        params.maxThreshold = maxthresh #220.0
 
        params.filterByArea = True
        params.minArea = 100
        params.maxArea = 1000
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
        keypoints = detector.detect(img);
        
        # cull keypoints far from the centroid
        prevlen = len(keypoints)
        if len(keypoints)>1:
            # uses Welford's algorithm for mean and variance
            k = 0 # count
            mcx=0 # mean centroid x
            mcy=0 # mean centroid y
            scx=0 # sum centroid x variance
            scy=0 # sum centroid y variance
            for p in keypoints:
                x = p.pt[0]
                y = p.pt[1]
                k+=1

                m = mcx+(x-mcx)/k
                scx += (x - mcx)*(x - m)
                mcx = m
                m = mcy+(y-mcy)/k
                scy += (y - mcy)*(y - m)
                mcy = m
            # get standard deviations
            sdx = math.sqrt(scx/(k-1))
            sdy = math.sqrt(scy/(k-1))
            
            # cull points which are more than 10 SDs away
            sdx*=10
            sdy*=10

            keypoints = [p for p in keypoints if \
                abs(p.pt[0]-mcx)<sdx and abs(p.pt[0]-mcy)<sdy ]

        
        count = len(keypoints)
        print(maxthresh,count)
        print("Culled {} points".format(prevlen-count))
        for p in keypoints:
            print(p.pt,p.size)
        if count<=8 and count>bestcount:
            count=bestcount
            bestpoints=keypoints
        

    keypoints=bestpoints        
    print(keypoints)
    img = cv.drawKeypoints(img, keypoints, 
            None, (255, 0, 0), 
            cv.DrawMatchesFlags_DRAW_RICH_KEYPOINTS )
    return(img,keypoints)

# each stage goes in here, they are all functions which take and return an (image,data) tuple
# Images are numpy/cv, and are either (x,y) or (x,y,3) ubyte arrays --- 8 bit and
# 24 bit colour respectively.

stages= [ ellipseDetect ]

# run stage n: each stage takes and returns an image

def stage(n,input):
    if n<len(stages):
        return stages[n](input)
    else:
        return img
    

