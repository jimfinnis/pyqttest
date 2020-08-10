# contrast stretch. Everything below tol (0-0.5) and 1-tol is clamped,
# and the rest is stretched. So if you do tol=0.2, you get a stretch
# of 0.2 to 0.8. 

def contrast(img,tol):
    B = img.astype(np.float)
    for b in range(3):
        print("BEEP",100*tol,100-100*tol)
            # find lower and upper limit for contrast stretching
        low, high = np.percentile(B[:,:,b], 100*tol), np.percentile(B[:,:,b], 100-100*tol)
        B[B<low] = low
        B[B>high] = high
        # ...rescale the color values to 0..255
    B[:,:,b] = 255 * (B[:,:,b] - B[:,:,b].min())/(B[:,:,b].max() - B[:,:,b].min())
    return (B.astype(np.uint8),None,False)


# histogram equalization
def equalise(img):
    r,g,b = cv.split(img)
    r = cv.equalizeHist(r)
    g = cv.equalizeHist(g)
    b = cv.equalizeHist(b)
    img = cv.merge((r,g,b))

