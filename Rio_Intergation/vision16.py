from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np
import math
from networktables import NetworkTable
import datetime
	
class Target:
	def __init__(self):
		self.lower_HSV = np.array([])
		self.upper_HSV = np.array([])
		self.vertices_lower = 0
		self.vertices_upper = 0
		self.width = 0
		self.height = 0
		self.solidity_lower = 0
		self.solidity_upper = 0
		self.aspect_ratio_lower = 0
		self.aspect_ratio_upper = 0
		return
		
	def add_HSV_values(self, lower, upper):
		self.lower_HSV = lower
		self.upper_HSV = upper
		return
		
	def add_vertices(self, lower, upper):
		self.vertices_lower = lower
		self.vertices_upper = upper
		return
		
	def add_width_and_height(self, w, h):
		self.width = w
		self.height = h
		return
		
	def add_solidity(self, lower, upper):
		self.solidity_lower = lower
		self.solidity_upper = upper
		return
		
	def add_aspect_ratio(self, lower, upper):
		self.aspect_ratio_lower = lower
		self.aspect_ratio_upper = upper
		return



def camera_initialise(framerate,resolutionX, resolutionY,shutterspeed,iso):
	camera = PiCamera()
	camera.resolution = (resolutionX, resolutionY)
	camera.framerate = framerate
	camera.hflip = True
	rawCapture = PiRGBArray(camera, size=(resolutionX, resolutionY))
	time.sleep(1)
	camera.exposure_mode = 'off'
	camera.shutter_speed = shutterspeed
	camera.iso = iso

	return (camera, rawCapture)

def draw_box(imgOriginal):
	cv2.rectangle(imgOriginal,(10,10),(210,100),(0,0,0), -1)
	return imgOriginal
	
def show_center_data(listCenterX,listCenterY,imgOriginal,tgtStatus,vp):
	cX= 1280
	cY= 1280
	if len(listCenterX)>= 2:	
		if tgtStatus:
			cv2.putText(imgOriginal, "Targets Acquired", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 0, 255), 2)
		cX = int((listCenterX[0] + listCenterX[1])/2)
		cY = int((listCenterY[0] + listCenterY[1])/2)
		(startX, endX) = (int(cX - 5), int(cX + 5))
		(startY, endY) = (int(cY - 5), int(cY + 5))
		cv2.line(imgOriginal, (startX, cY), (endX, cY), (0, 0, 255), 3)
		cv2.line(imgOriginal, (cX, startY), (cX, endY), (0, 0, 255), 3)

		cv2.putText(imgOriginal, ("Ctr X = " + str(cX)), (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 0, 255), 1)
		cv2.putText(imgOriginal, ("Ctr Y = " + str(cY)), (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 0, 255), 1)
	
	else:
		cX = 0
		cY = 0
		cv2.putText(imgOriginal, ("Ctr X = "), (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 0, 255), 1)
		cv2.putText(imgOriginal, ("Ctr Y = "), (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 0, 255), 1)
	vp.putNumber("cX", cX)
	vp.putNumber("cY", cY)
	
	return imgOriginal, cX, cY

def show_dist_data(imgOriginal, listCenterX,vp): # pixels to inches
	tgtDist=-1
	if len(listCenterX)>= 2:	
		horiLine = listCenterX[1]- listCenterX[0]
		if horiLine > 0:
			tgtDist = 5123.3 * (math.pow((abs(horiLine)),(-1)))
		else:
			tgtDist = 0
		tgtDist = float(round(tgtDist,2))
		cv2.putText(imgOriginal, ("Dist to Target  = " + str(tgtDist)), (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 255, 0), 1)
		#sends value out to the NetworkTable
	else :
		cv2.putText(imgOriginal, ("Dist to Target = "), (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 0, 255), 1)
	
	vp.putNumber("tgtDist",tgtDist)	
	return imgOriginal
	
def show_widhi_data(imgOriginal, listCenterX, aw, ah):
	if len(listCenterX)>= 2:
		cv2.putText(imgOriginal, ("Width = " + str(aw)), (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 255, 0), 1)
		cv2.putText(imgOriginal, ("Height = " + str(ah)), (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 255, 0), 1) 
	else:
		cv2.putText(imgOriginal, ("Width = "), (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 255, 0), 1)
		cv2.putText(imgOriginal, ("Height = "), (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 255, 0), 1) 
	return imgOriginal
	
def center_of_contour(imgOriginal,approx,w,h,M,listCenterX,listCenterY,draw):
	(cX, cY) = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
	(startX, endX) = (int(cX - (w * 0.15)), int(cX + (w * 0.15)))
	(startY, endY) = (int(cY - (h * 0.15)), int(cY + (h * 0.15)))
	listCenterX.append(cX)
	listCenterY.append(cY)
	if draw:
		cv2.line(imgOriginal, (startX, cY), (endX, cY), (0, 0, 255), 3)
		cv2.line(imgOriginal, (cX, startY), (cX, endY), (0, 0, 255), 3)
	return listCenterX, listCenterY, imgOriginal
	
def outline_rectangle_red(imgOriginal, approx):
	cv2.drawContours(imgOriginal, [approx], -1, (0, 0, 255), 4)
	return imgOriginal

def bounding_rectangle_blue(imgOriginal,c):
	rect = cv2.minAreaRect(c)
	box = cv2.boxPoints(rect)
	box = np.int0(box)
	cv2.drawContours(imgOriginal,[box],0,(255,0,0),2)
	ax,ay,aw,ah = cv2.boundingRect(c)
	cv2.rectangle(imgOriginal,(ax,ay),(ax+aw,ay+ah),(0,255,0),2)
	return ax,ay,aw,ah,imgOriginal
	
def calc_percent_error_X(resolutionX, listCenterX,theoCenterX):
	center = resolutionX/2+theoCenterX
	if len(listCenterX) >1:
		cX = float(listCenterX[0] + listCenterX[1])/2
		errorX =float(((cX-center)/center)*100)
		errorX = round(errorX,2)
	else :
                errorX = 101
	return errorX

def disp_percent_error_X(imgOriginal, errorX,listCenterX,vp):
	
	cv2.putText(imgOriginal, ("% ErrorX = " + str(errorX)), (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 255, 0), 1)
	vp.putNumber("errorX", errorX)
	return imgOriginal


def calc_percent_error_Y(resolutionY, listCenterY,theoCenterY):
	center = resolutionY/2+theoCenterY
	if len(listCenterY) >1:
		cY = float(listCenterY[0] + listCenterY[1])/2
		errorY =float(((cY-center)/center)*100)
		errorY = round(errorY,2)
	else :
                errorY = 101
	
	return errorY

def disp_percent_error_Y(imgOriginal, errorY,listCenterY,vp):
	
	cv2.putText(imgOriginal, ("% ErrorY = " + str(errorY)), (20, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 255, 0), 1)
	vp.putNumber("errorY", errorY)
	return imgOriginal
	
def show_angle_data(listArea, listCenterX,imgOriginal,vp):
	tgtAng = 360
	if len(listArea) > 1:
		diffSizeCont = ((listArea[1]-listArea[0])/listArea[0])*100
		tgtAng = 10.456*(math.sqrt(abs(diffSizeCont)))
		tgtAng = tgtAng - 26.9
		tgtAng = float(round(tgtAng,0))
		if listCenterX[1]>listCenterX[0]:
			tgtAng = -tgtAng
		
		cv2.putText(imgOriginal, ("Angle = " + str(tgtAng)), (20, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 255, 0), 1)
		vp.putNumber("tgtAng", tgtAng)
	else:
		cv2.putText(imgOriginal, ("Angle = "), (20, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 255, 0), 1)
		vp.putNumber("tgtAng", tgtAng)
	
	return imgOriginal
	

def sendTime(vp,startTime):
	#t = datetime.datetime.now()
	elapsedTime = time.time() - startTime
	#vp.putNumber("minutes",t.minute)
	vp.putNumber("seconds",elapsedTime)
	
def init_network_tables(ipAddress, table):
	NetworkTable.setIPAddress(ipAddress)
	NetworkTable.setClientMode()
	NetworkTable.initialize()
	vp=NetworkTable.getTable(table)
	return vp

def findShapes(cnts, target, imgOriginal,draw):
	#save center values
	listCenterX = []
	listCenterY = []
	listArea = []
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
				listArea.append(area)
				M = cv2.moments(approx)
				tgtStatus = True
				vp.putBoolean("tgtStatus", tgtStatus)
				listCenterX, listCenterY, imgOriginal = center_of_contour(imgOriginal,approx,w,h,M,listCenterX,listCenterY,draw)
				if draw:
					# draw an outline around the target and update the status
					# text
					imgOriginal = outline_rectangle_red(imgOriginal, approx)
				
			
					# compute the center of the contour region and draw the
					# crosshairs
					ax,ay,aw,ah = cv2.boundingRect(c)
					cv2.rectangle(imgOriginal,(ax,ay),(ax+aw,ay+ah),(0,255,0),2)
				
	return listArea, listCenterX, listCenterY