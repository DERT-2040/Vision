from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np
import math
import vision21 as vision
from networktables import NetworkTable

#set up tables
ipAddress = "192.168.1.110"
table = "Vision"

#initialise the camera
framerate = 5
resolutionX = 640
resolutionY = 480
shutterspeed = 500
iso = 500
camera,rawCapture = vision.camera_initialise(framerate,resolutionX,resolutionY,shutterspeed,iso)
vp = vision.init_network_tables(ipAddress, table)

#settings for low target
target = vision.Target()
target.add_HSV_values(np.array([40,80,70]), np.array([80, 200,255]))
target.add_vertices(4,10)
target.add_width_and_height(5,5)
target.add_solidity(0.4,1)
target.add_aspect_ratio(.2,1)
h = 0
s = 0
v = 0
# allow the camera to warmup
time.sleep(0.1)
# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	# grab the raw NumPy array representing the image, then initialize the timestamp
	# and occupied/unoccupied text
	imgOriginal = frame.array
	
	key = cv2.waitKey(1) & 0xFF
	
	#this is set to work with the gear targets. The image size and solidity need to be changed to work with other targets
	status = "No Targets"
	
	#change the name of the image file as needed. File needs to be in the same directory as the script
	imgHSV = cv2.cvtColor(imgOriginal, cv2.COLOR_BGR2HSV)
	h = 0 
	break1 = 0
	break2 = break1
	# for reflective tape with our green medusa 
	for h in range(0,100):
		
		for s in range(0,255):
			
			for v in range(0,255):
				if key == ord("q"):
					break
				if h< 15:
					target.add_HSV_values(np.array([0,0,0]), np.array([h, s,v]))
				else:
					target.add_HSV_values(np.array([h-15,s-15,v-15]), np.array([h,s,v]))
					
				
				
				imgThresh = cv2.inRange(imgHSV, target.lower_HSV, target.upper_HSV)
				imgThresh2 = imgThresh
				#cv2.imshow('imgThresh2', imgThresh2)
				cv2.imwrite('imgThresh', imgThresh2)
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
						x, y, w, h = cv2.boundingRect(approx)
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
							# draw an outline around the target and update the status
							# text
							imgOriginal = vision.outline_rectangle_red(imgOriginal, approx)
							status = "Target(s) Acquired"
				 
							# compute the center of the contour region and draw the
							# crosshairs
							M = cv2.moments(approx)
							listCenterX, listCenterY, imgOriginal = vision.center_of_contour(imgOriginal,approx,w,h,M,listCenterX,listCenterY)
							ax,ay,aw,ah = cv2.boundingRect(c)
							cv2.rectangle(imgOriginal,(ax,ay),(ax+aw,ay+ah),(0,255,0),2)
							
			if key == ord("q"):
				break1= 1
				break				
			v +=10
		if break1 == 1:
			break2 =1
			break
		s+=10
	if break2 == 1:
		break
	h+=10
	# draw the status text on the frame	
	imgOriginal = vision.draw_box(imgOriginal)
	imgOriginal,cX,cY = vision.show_center_data(listCenterX,listCenterY,imgOriginal,status,vp)
	imgOriginal = vision.show_dist_data(imgOriginal,listCenterX,vp)
	errorX = vision.calc_percent_error_X(resolutionX, listCenterX)
	imgOriginal = vision.disp_percent_error_X(imgOriginal, errorX,listCenterX,vp)
	del listCenterX[:]
	del listCenterY[:]
	
	# clear the stream in preparation for the next frame
	#cv2.imshow("Frame", imgOriginal)
	key = cv2.waitKey(1) & 0xFF
	rawCapture.truncate(0)
 
	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break

camera.close()
cv2.destroyAllWindows()
