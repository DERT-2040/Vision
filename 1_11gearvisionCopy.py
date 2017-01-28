import cv2
import numpy as np
#from matplotlib import pyplot as plt
#this is set to work with the "green U" printed targets. The image size and solidity need to be changed to work with the 2105 FRC images
status = "No Targets"
#change the name of the image fike as needed. File needs to be in the same directory as the script
#a few lines of code will make this into a video capture.
imgOriginal = cv2.imread('gear_3.jpg') 
#gray = cv2.cvtColor(imgOriginal, cv2.COLOR_BGR2GRAY)
#cv2.imshow('gray', gray)
#ret, graythresh = cv2.threshold(gray,85,255,cv2.THRESH_BINARY)
#cv2.imshow('graythresh',graythresh)
imgHSV = cv2.cvtColor(imgOriginal, cv2.COLOR_BGR2HSV)

#imgThresh = cv2.inRange(imgHSV, np.array([70, 80, 100]), np.array([95, 255, 255]))
imgThresh = cv2.inRange(imgHSV, np.array([40,100,100]), np.array([90, 255, 255]))
# for the dark gren  target
imgThresh2 = imgThresh
cv2.imshow('imgThresh2', imgThresh2)
#imgBlur = cv2.GaussianBlur(imgThresh, (3, 3), 2)
#imgBlur2=imgBlur
#cv2.imshow('imgBlur2', imgBlur2)
#imgErode = cv2.erode(imgBlur, np.ones((5,5),np.uint8))
#imgDilate = cv2.dilate(imgThresh, np.ones((5,5),np.uint8))
#edged = cv2.Canny(gray, 50, 150)
# find contours in the edge map
(im2, cnts, hierarchy) = cv2.findContours(imgThresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#cv2.imshow('edged', edged)	

#save center values
listCenterX = [];
listCenterY = [];

# loop over the contours
for c in cnts:
	# approximate the contour
	peri = cv2.arcLength(c, True)
	approx = cv2.approxPolyDP(c, 0.01 * peri, True)
 
	# ensure that the approximated contour is "roughly" rectangular
	if len(approx) >= 4 and len(approx) <= 10:
		# compute the bounding box of the approximated contour and
	        # use the bounding box to compute the aspect ratio
		(x, y, w, h) = cv2.boundingRect(approx)
		aspectRatio = w / float(h)
 
		# compute the solidity of the original contour
		area = cv2.contourArea(c)
		hullArea = cv2.contourArea(cv2.convexHull(c))
		solidity = area / float(hullArea)
		 
		# compute whether or not the width and height, solidity, and
		# aspect ratio of the contour falls within appropriate bounds
		keepDims = w > 5 and h >5
		#the U shaped targets are not very "solid" so a small number helps prevet false positives
		keepSolidity = solidity > 0.4 and solidity < 1
		keepAspectRatio = aspectRatio >= .2  and aspectRatio <= 4
		
		# ensure that the contour passes all our tests
		if keepDims and keepSolidity and keepAspectRatio:
			# draw an outline around the target and update the status
			# text
			cv2.drawContours(imgOriginal, [approx], -1, (0, 0, 255), 4)
			status = "Target(s) Acquired"
 
			# compute the center of the contour region and draw the
			# crosshairs
			M = cv2.moments(approx)
			(cX, cY) = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
			(startX, endX) = (int(cX - (w * 0.15)), int(cX + (w * 0.15)))
			(startY, endY) = (int(cY - (h * 0.15)), int(cY + (h * 0.15)))
			listCenterX.append(cX)
			listCenterY.append(cY)
			cv2.line(imgOriginal, (startX, cY), (endX, cY), (0, 0, 255), 3)
			cv2.line(imgOriginal, (cX, startY), (cX, endY), (0, 0, 255), 3)

			#bounding rectangle test
			rect = cv2.minAreaRect(c)
			box = cv2.boxPoints(rect)
			box = np.int0(box)
			cv2.drawContours(imgOriginal,[box],0,(255,0,0),2)

			ax,ay,aw,ah = cv2.boundingRect(c)
			cv2.rectangle(imgOriginal,(ax,ay),(ax+aw,ay+ah),(0,255,0),2)
			target_actual_width = 6.77
			calc_tgt_dist = target_actual_width * 643 / aw
# draw the status text on the frame
cv2.putText(imgOriginal, status, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 0, 255), 2)
cX = int((listCenterX[0] + listCenterX[1])/2)
cY = int((listCenterY[0] + listCenterY[1])/2)
(startX, endX) = (int(cX - 5), int(cX + 5))
(startY, endY) = (int(cY - 5), int(cY + 5))
cv2.line(imgOriginal, (startX, cY), (endX, cY), (0, 0, 255), 3)
cv2.line(imgOriginal, (cX, startY), (cX, endY), (0, 0, 255), 3)
#cv2.putText(imgOriginal, ("Ctr X = " + str(cX)), (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 0, 255), 1)
#cv2.putText(imgOriginal, ("Ctr Y = " + str(cY)), (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 0, 255), 1)
#cv2.putText(imgOriginal, ("Width = " + str(aw)), (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 255, 0), 1)
#cv2.putText(imgOriginal, ("Height = " + str(ah)), (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 255, 0), 1) 
#cv2.putText(imgOriginal, ("Distance to Target  = " + str(calc_tgt_dist)), (20, 430), cv2.FONT_HERSHEY_SIMPLEX, 0.8,(255, 0, 0), 2)

#ret,thresh = cv2.threshold(gray,127,255,0)
#im2, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

#cnt = contours[4]
#cv2.drawContours(imgOriginal, [cnt], 0, (0,255,0), 3)

#cv2.imshow('img2', im2)

cv2.imshow('imgOriginal',imgOriginal)
#cv2.imshow('imgThresh', imgThresh)
#cv2.imshow('imgDilate', imgDilate)
cv2.waitKey(0)
cv2.destroyAllWindows()
