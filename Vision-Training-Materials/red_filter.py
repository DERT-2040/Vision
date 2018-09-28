#color_filter2 is a combination of the procession from OpenCV-test3.py and the one from the pythonprograming.net tutorials on sentdex
#from pythonprogramming.net
#use a still image and this website to help tuns HSV http://imagecolorpicker.com/
import cv2
import numpy as np

cap = cv2.VideoCapture(0)

while(1):
    _, imOriginal = cap.read()
    imgHSV = cv2.cvtColor(imOriginal, cv2.COLOR_BGR2HSV)
    #reds exist on both side os "zero" in HSV. This is solved with two arrays one
    #is called "low" and the other "high" later they are added together.
    # HSV O, 135, 135 in openCV converts to 0, 53,53 is regular HSV which is 133,64,64 in RGB it is a dark maroon
    # HSV 18, 255, 255 in openCV converts to 36, 100, 100 in regular HSV which is 255, 153, 0 it is orange
    # HSV 165, 135, 135 in open CV converts to 330, 53,53 in regular HSV whuck is 135, 64, 00 it is purple
    # HSV 179, 255, 255 in openCV converts to 358, 100, 100 in regular HSV which is 255,0,8 it is bright red.   
    imgThreshLow = cv2.inRange(imgHSV, np.array([0, 135, 135]), np.array([18, 255, 255]))
    imgThreshHigh = cv2.inRange(imgHSV, np.array([165, 135, 135]), np.array([179, 255, 255]))
    #cv2.imshow("imgThreshLow", imgThreshLow)                       # test line to see LOW Threshhold
    #cv2.imshow("imgThreshHigh", imgThreshHigh)                     # test line to see High Threshold

    imgThresh = cv2.add(imgThreshLow, imgThreshHigh)

    imgThresh = cv2.GaussianBlur(imgThresh, (3, 3), 2)

    imgThresh = cv2.dilate(imgThresh, np.ones((5,5),np.uint8))
    imgThresh = cv2.erode(imgThresh, np.ones((5,5),np.uint8))


    ###########################3
      
        
    #imshow section

    cv2.imshow('Original',imOriginal)
    cv2.imshow('imgThreshg',imgThresh)
    #cv2.imshow("imgHSV", imgHSV)                                   # just to see what an HSV image looks like    

    
    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

cv2.destroyAllWindows()
cap.release()
