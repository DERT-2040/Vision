from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np
import math
import vision


#initialise the camera

framerate = 5
camera,rawCapture = vision.camera_initialise(framerate)

#settings for low target
target = vision.Target()
target.add_HSV_values(np.array([40,100,100]), np.array([90, 255, 255]))
target.add_vertices(4,10)
target.add_width_and_height(5,5)
target.add_solidity(0.4,1)
target.add_aspect_ratio(.2,1)

# allow the camera to warmup
time.sleep(0.1)

# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	# grab the raw NumPy array representing the image, then initialize the timestamp
	# and occupied/unoccupied text
	imgOriginal = frame.array
	
	#this is set to work with the gear targets. The image size and solidity need to be changed to work with other targets
	status = "No Targets"
	
	#change the name of the image file as needed. File needs to be in the same directory as the script
	imgHSV = cv2.cvtColor(imgOriginal, cv2.COLOR_BGR2HSV)
	
	# for reflective tape with our green medusa 
	imgThresh = cv2.inRange(imgHSV, target.lower_HSV, target.upper_HSV)
	imgThresh2 = imgThresh
	cv2.imshow('imgThresh2', imgThresh2)
	
	# find contours in the edge map
	(im2, cnts, hierarchy) = cv2.findContours(imgThresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)	

	#save center values
	listCenterX = []
	listCenterY = []
	
	
	# loop over the contours
	for c in cnts:
		# approximate the contour
		peri = cv2.arcLength(c, True)
		approx = cv2.approxPolyDP(c, 0.01 * peri, True)
	 
		# ensure that the approximated contour is "roughly" rectangular
		if len(approx) >= target.vertices_lower and len(approx) <= target.vertices_upper:
			# compute the bounding box of the approximated contour and
			# use the bounding box to compute the aspect ratio
			(x, y, w, h) = cv2.boundingRect(approx)
			aspectRatio = w / float(h)
	 
			# compute the solidity of the original contour
			area = cv2.contourArea(c)
			hullArea = cv2.contourArea(cv2.convexHull(c))
			solidity = area / float(hullArea)
			 
			# compute whether or not the width and height, solidity, and aspect ratio of the contour falls within appropriate bounds
			keepDims = w > target.width and h > target.height
			keepSolidity = solidity > target.solidity_lower and solidity < target.solidity_upper
			keepAspectRatio = aspectRatio >= target.aspect_ratio_lower and aspectRatio <= target.aspect_ratio_upper
			
			# ensure that the contour passes all our tests
			if keepDims and keepSolidity and keepAspectRatio:
				status = "Target(s) Acquired"
				vision.outline_rectangle_red(imgOriginal, approx)
				ax,ay,aw,ah = vision.bounding_rectangle_blue(imgOriginal,c)
				listCenterX, listCenterY = vision.center_of_contour(imgOriginal,approx,w,h)
	# draw the status text on the frame	
	vision.draw_box(imgOriginal)
	vision.show_center_data(listCenterX,listCenterY,imgOriginal)
	vision.show_dist_data(imgOriginal,listCenterX)
	
	del listCenterX[:]
	del listCenterY[:]

	# clear the stream in preparation for the next frame
	cv2.imshow("Frame", imgOriginal)
	key = cv2.waitKey(1) & 0xFF
	rawCapture.truncate(0)
 
	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break

camera.close()
cv2.destroyAllWindows()
