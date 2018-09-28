# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 5
camera.hflip = True

rawCapture = PiRGBArray(camera, size=(640, 480))

# allow the camera to warmup
time.sleep(0.1)

# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        # grab the raw NumPy array representing the image, then initialize the timestamp
        # and occupied/unoccupied text
        imOriginal = frame.array

        
        imgHSV = cv2.cvtColor(imOriginal,cv2.COLOR_BGR2HSV)
        imgThreshLow = cv2.inRange(imgHSV, np.array([0, 204, 204]), np.array([18, 255, 255]))
        imgThreshHigh = cv2.inRange(imgHSV, np.array([165, 135, 135]), np.array([179, 255, 255]))
        
        imgThresh = cv2.add(imgThreshLow, imgThreshHigh)

        imgThresh = cv2.GaussianBlur(imgThresh, (3, 3), 2)

        imgThresh = cv2.dilate(imgThresh, np.ones((5,5),np.uint8))
        imgThresh = cv2.erode(imgThresh, np.ones((5,5),np.uint8))


    #########################  
        cv2.imshow('Original',imOriginal)
        cv2.imshow('imgThreshg',imgThresh)       #cv2.imshow("imgHSV", imgHSV)                                   # just to see what an HSV image looks like  
        cv2.imshow('ingHSV', imgHSV)
        
        key = cv2.waitKey(1) & 0xFF

        # clear the stream in preparation for the next frame
        rawCapture.truncate(0)

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
                brea
