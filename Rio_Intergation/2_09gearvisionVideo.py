from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np
import math
import vision29 as vision
from networktables import NetworkTable
	#import getKey

try:
	#set up tables
	ipAddress = "192.168.1.110"
	table = "Vision"
	startTime = time.time()
	#initialise the camera
	framerate = 10
	resolutionX = 640
	resolutionY = 480
	shutterspeed = 500
	iso = 500
	camera,rawCapture = vision.camera_initialise(framerate,resolutionX,resolutionY,shutterspeed,iso)
	vp = vision.init_network_tables(ipAddress, table)
	runHeaded = False

	#settings for low target
	target = vision.Target()
	target.add_HSV_values(np.array([25,130,10]), np.array([75, 255,200]))
	target.add_vertices(4,7)
	target.add_width_and_height(5,5)
	target.add_solidity(0.4,1)
	target.add_aspect_ratio(.2,1)
	theoCenterX = 0
	theoCenterY = 0


	# allow the camera to warmup
	time.sleep(0.1)
	noOfFrames = 20
	# capture frames from the camera
	while True:
		listActCenterX = []
		listActCenterY = []
		listErrorX = []
		listErrorY = []
		listDist = []
		listAngle = []
		i = 0
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
			if runHeaded:
				cv2.imshow('imgThresh2', imgThresh2)
			
			# find contours in the edge map
			(im2, cnts, hierarchy) = cv2.findContours(imgThresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)	

			#save center values
			listCenterX = []
			listCenterY = []
			listArea = []
			
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
						tgtStatus = True
			 
						# compute the center of the contour region and draw the
						# crosshairs
						M = cv2.moments(approx)
						listCenterX, listCenterY, imgOriginal = vision.center_of_contour(imgOriginal,approx,w,h,M,listCenterX,listCenterY)
						ax,ay,aw,ah = cv2.boundingRect(c)
						cv2.rectangle(imgOriginal,(ax,ay),(ax+aw,ay+ah),(0,255,0),2)
						listArea.append(area)
			
						
			# draw the status text on the frame	
			imgOriginal = vision.draw_box(imgOriginal)
			imgOriginal,actCenterX,actCenterY = vision.show_center_data(listCenterX,listCenterY,imgOriginal,tgtStatus,vp)
			listActCenterX.append(actCenterX)
			listActCenterY.append(actCenterY)
			dist = vision.show_dist_data(imgOriginal, listCenterX,vp)
			listDist.append(dist)
			imgOriginal,tgtAng = vision.show_angle_data(listArea, listCenterX,imgOriginal,vp)
			listAngle.append(tgtAng)
			
			#draw errorX and errorY
			errorX = vision.calc_percent_error_X(resolutionX, listCenterX,theoCenterX)
			listErrorX.append(errorX)
			imgOriginal = vision.disp_percent_error_X(imgOriginal, errorX,listCenterX,vp)
			errorY = vision.calc_percent_error_Y(resolutionY, listCenterY,theoCenterY)
			listErrorY.append(errorY)
			imgOriginal = vision.disp_percent_error_Y(imgOriginal, errorY,listCenterY,vp)
			vision.sendTime(vp, startTime);
			
			if runHeaded:
				cv2.imshow("Frame", imgOriginal)
			del listCenterX[:]
			del listCenterY[:]
			del listArea[:]
			
			rawCapture.truncate(0)
			if i > 5:
				break
			i += 1
			
			
			
			
		#display and put numbers
		counter = 0;
		j = 0
		while (j < len(listActCenterX)-1):
			if (0 > listDist[j]):
				("one more counter")
				counter += 1
			j+=1
		k = 0
		if counter > 4:
			
			vp.putBoolean("tgtStatus",False)
			vp.putNumber("cY",1280)
			vp.putNumber("cX",1280)
			vp.putNumber("tgtDist",-1)	
			vp.putNumber("errorX", 101)
			vp.putNumber("errorY", 101)
			vp.putNumber("tgtAng", 360)
		else:
			totalCX = listActCenterX[k]
			totalCY = listActCenterY[k]
			totalTgtDist = listDist[k]
			totalErrorX =	listErrorX[k]
			totalErrorY =	listErrorY[k]
			totalTgtAng = listAngle[k]
			totalCounted = 1
			totalCounted = 0;
			vp.putBoolean("tgtStatus",True)
			while k < len(listActCenterX)-1:
				if (0 <= listDist[k]):
					totalCX += listActCenterX[k]
					totalCY += listActCenterY[k]
					totalTgtDist += listDist[k]
					totalErrorX +=	listErrorX[k]
					totalErrorY +=	listErrorY[k]
					totalTgtAng += listAngle[k]
					totalCounted += 1
				k+=1
			totalCX /= totalCounted
			totalCY /= totalCounted
			totalTgtDist /= totalCounted
			totalErrorX /=	totalCounted
			totalErrorY /=	totalCounted
			totalTgtAng /= totalCounted
			
			vp.putNumber("cY",totalCY)
			vp.putNumber("cX",totalCX)
			vp.putNumber("tgtDist",totalTgtDist)	
			vp.putNumber("errorX", totalErrorX)
			vp.putNumber("errorY", totalErrorY)
			vp.putNumber("tgtAng", totalTgtAng)
			
except KeyboardInterrupt:
	camera.close()
	cv2.destroyAllWindows()
 
