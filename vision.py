from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np
import math

def camera_initialise(framerate):
	camera = PiCamera()
	camera.resolution = (640, 480)
	camera.framerate = framerate
	camera.hflip = True
	rawCapture = PiRGBArray(camera, size=(640, 480))
	return (camera, rawCapture)

def draw_box(imgOriginal):
	cv2.rectangle(imgOriginal,(10,10),(210,100),(0,0,0), -1)
	return imgOriginal
	
def show_center_data(listCenterX,listCenterY,imgOriginal,status):
	if len(listCenterX)>= 2:	
		cv2.putText(imgOriginal, status, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 0, 255), 2)
		cX = int((listCenterX[0] + listCenterX[1])/2)
		cY = int((listCenterY[0] + listCenterY[1])/2)
		(startX, endX) = (int(cX - 5), int(cX + 5))
		(startY, endY) = (int(cY - 5), int(cY + 5))
		cv2.line(imgOriginal, (startX, cY), (endX, cY), (0, 0, 255), 3)
		cv2.line(imgOriginal, (cX, startY), (cX, endY), (0, 0, 255), 3)

		cv2.putText(imgOriginal, ("Ctr X = " + str(cX)), (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 0, 255), 1)
		cv2.putText(imgOriginal, ("Ctr Y = " + str(cY)), (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 0, 255), 1)
	else:
		cv2.putText(imgOriginal, ("Ctr X = "), (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 0, 255), 1)
		cv2.putText(imgOriginal, ("Ctr Y = "), (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 0, 255), 1)
	return imgOriginal

def show_dist_data(imgOriginal, listCenterX): # pixels to inches
	if len(listCenterX)>= 2:	
		horiLine = abs(listCenterX[1]- listCenterX[0])
		calc_tgt_dist = 109.3 * (math.pow((1-0.0075145),(horiLine)))
		calc_tgt_dist = round(calc_tgt_dist,2)
		cv2.putText(imgOriginal, ("Dist to Target  = " + str(calc_tgt_dist)), (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 255, 0), 1)
	else :
		cv2.putText(imgOriginal, ("Dist to Target  = "), (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 255, 0), 1)
	return imgOriginal
	
def show_widhi_data(imgOriginal, listCenterX, aw, ah):
	if len(listCenterX)>= 2:
		cv2.putText(imgOriginal, ("Width = " + str(aw)), (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 255, 0), 1)
		cv2.putText(imgOriginal, ("Height = " + str(ah)), (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 255, 0), 1) 
	else:
		cv2.putText(imgOriginal, ("Width = "), (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 255, 0), 1)
		cv2.putText(imgOriginal, ("Height = "), (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 255, 0), 1) 
	return imgOriginal
	
def center_of_contour(imgOriginal,approx,w,h,M,listCenterX,listCenterY):
	(cX, cY) = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
	(startX, endX) = (int(cX - (w * 0.15)), int(cX + (w * 0.15)))
	(startY, endY) = (int(cY - (h * 0.15)), int(cY + (h * 0.15)))
	listCenterX.append(cX)
	listCenterY.append(cY)
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