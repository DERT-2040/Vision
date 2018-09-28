from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np
import math
import vision16 as vision
from networktables import NetworkTable
	#import getKey

try:
	#set up tables
	ipAddress = "10.20.40.65"
	table = "Vision"
	startTime = time.time()
	#initialise the camera
	framerate = 15
	resolutionX = 640
	resolutionY = 480
	shutterspeed = 250
	iso = 250
	camera,rawCapture = vision.camera_initialise(framerate,resolutionX,resolutionY,shutterspeed,iso)
	vp = vision.init_network_tables(ipAddress, table)
	runHeaded = True

	#settings for low target
	target = vision.Target()
	target.add_HSV_values(np.array([25,130,10]), np.array([75, 255,200]))
	target.add_vertices(4,12)
	target.add_width_and_height(10,10)
	target.add_solidity(0.2,1)
	target.add_aspect_ratio(.2,.6)
	theoCenterX = 0
	theoCenterY = 0


	# allow the camera to warmup
	time.sleep(0.1)

	# capture frames from the camera
	for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
		# grab the raw NumPy array representing the image, then initialize the timestamp
		# and occupied/unoccupied text
		
		imgOriginal = frame.array
		imgOriginal=cv2.flip(imgOriginal,1)
		#this is set to work with the gear targets. The image size and solidity need to be changed to work with other targets
		tgtStatus = False
		
		#change the name of the image file as needed. File needs to be in the same directory as the script
		imgHSV = cv2.cvtColor(imgOriginal, cv2.COLOR_BGR2HSV)
		
		# for reflective tape with our green medusa 
		imgThresh = cv2.inRange(imgHSV, target.lower_HSV, target.upper_HSV)
		imgThresh2 = imgThresh
		kernel = np.ones((50,1),np.float32)/50
		imgThresh = cv2.filter2D(imgThresh,-1,kernel)
		imgThresh = cv2.inRange(imgThresh,75,255)
		cv2.imshow('imgThresh', imgThresh)
		# find contours in the edge map
		(im2, cnts, hierarchy) = cv2.findContours(imgThresh2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)	
		listArea, listCenterX,listCenterY = vision.findShapes(cnts, target, imgOriginal, False)
		(im2, cnts, hierarchy) = cv2.findContours(imgThresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		listAreaBlur, listCenterXBlur,listCenterYBlur = vision.findShapes(cnts, target, imgOriginal, True)
		position = "No Target"
		avg = 0;
		centerX = 1;
		if len(listCenterXBlur)>1 and len(listCenterX) > 1:
			if listArea[0] > listArea[1]:
				centerX = listCenterX[0]
			else:
				centerX = listCenterX[1]
		elif len(listCenterX) > 1:
			centerX = listCenterX[0]
		if len(listCenterXBlur)>1 and len(listCenterX) >= 1 :	
			l = 0
			if listCenterXBlur[1] > listCenterXBlur[0] and listCenterXBlur[1] > (centerX+10) and listCenterXBlur[1] > (centerX-10):
				position = "Right"
			elif listCenterXBlur[1] > listCenterXBlur[0] and listCenterXBlur[1] < (centerX+10) and listCenterXBlur[1] < (centerX-10):
				position = "Left"
			elif listCenterXBlur[1] < listCenterXBlur[0] and listCenterXBlur[1] > (centerX+10) and listCenterXBlur >  (centerX-10):
				position = "Right"
			elif listCenterXBlur[1] < listCenterXBlur[0] and listCenterXBlur[1] < (centerX+10) and listCenterXBlur <  (centerX-10):
				position = "Left"
			else:
				position = "Center"
		
		
		listCenterY = listCenterYBlur
		listCenterX = listCenterXBlur
		listArea = listAreaBlur
					
		
		# loop over the contours
		# draw the status text on the frame	
		imgOriginal = vision.draw_box(imgOriginal)
		imgOriginal,cX,cY = vision.show_center_data(listCenterX,listCenterY,imgOriginal,tgtStatus,vp)
		imgOriginal = vision.show_dist_data(imgOriginal,listCenterX,vp)
		imgOriginal = vision.show_angle_data(listArea, listCenterX,imgOriginal,vp)
			
		#draw errorX and errorY
		errorX = vision.calc_percent_error_X(resolutionX, listCenterX,theoCenterX)
		imgOriginal = vision.disp_percent_error_X(imgOriginal, errorX,listCenterX,vp)
		errorY = vision.calc_percent_error_Y(resolutionY, listCenterY,theoCenterY)
		imgOriginal = vision.disp_percent_error_Y(imgOriginal, errorY,listCenterY,vp)
		cv2.putText(imgOriginal, ("Position = " + position), (20, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 255, 0), 1)
		vision.sendTime(vp, startTime);
			
		if runHeaded:
			cv2.imshow("Frame", imgOriginal)
				
			# clear the stream in preparation for the next frame
		del listCenterX[:]
		del listCenterY[:]
		key = cv2.waitKey(1) & 0xFF
		del listArea[:]
		if key == ord("q"):
			break
			
		rawCapture.truncate(0)
		
		
except KeyboardInterrupt:
	camera.close()
	cv2.destroyAllWindows()
	

 
