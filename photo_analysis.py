import cv2
import numpy as np
#from matplotlib import pyplot as plt

imgOriginal = cv2.imread('image.jpg') 
imgGray = cv2.cvtColor(imgOriginal, cv2.COLOR_BGR2GRAY)
ret, graythresh = cv2.threshold(imgGray,100,255,cv2.THRESH_BINARY)
imgHSV = cv2.cvtColor(imgOriginal, cv2.COLOR_BGR2HSV)
imgThresh = cv2.inRange(imgHSV, np.array([20,180,70]), np.array([40, 255, 200]))
#imgBlur = cv2.GaussianBlur(imgThresh, (3, 3), 2)
imgErode = cv2.erode(imgThresh, np.ones((5,5),np.uint8))
imgDilate = cv2.dilate(imgErode, np.ones((5,5),np.uint8))

#ret,thresh = cv2.threshold(gray,127,255,0)
#im2, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

#cnt = contours[4]
#cv2.drawContours(imgOriginal, [cnt], 0, (0,255,0), 3)

#cv2.imshow('immg2', im2)
cv2.imshow('graythresh', graythresh)
#cv2.imshow('Blur',imgBlur)
#cv2.imshow('Erode',imgErode)
cv2.imshow('imgOriginal',imgOriginal)
cv2.imshow('imgThresh', imgThresh)
#cv2.imshow('imgDilate', imgDilate)
cv2.waitKey(0)
cv2.destroyAllWindows()
