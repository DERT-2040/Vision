import cv2
import numpy as np
#from matplotlib import pyplot as plt
status = "No Targets"
imgOriginal = cv2.imread('2016_test_image_230.jpg') 
#gray = cv2.cvtColor(imgOriginal, cv2.COLOR_BGR2GRAY)
#cv2.imshow('gray', gray)
#ret, graythresh = cv2.threshold(gray,85,255,cv2.THRESH_BINARY)
#cv2.imshow('graythresh',graythresh)
imgHSV = cv2.cvtColor(imgOriginal, cv2.COLOR_BGR2HSV)

imgThresh = cv2.inRange(imgHSV, np.array([70, 80, 100]), np.array([95, 255, 255]))
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
		keepDims = w > 5 and h > 5
		keepSolidity = solidity > 0.01
		keepAspectRatio = aspectRatio >= 1  and aspectRatio <= 5
		print("x = "), (x), ("y ="), (y), ("w ="),(w), ("h ="),(h)
		print(("area"), (area))
		print("hullArea"), (hullArea)
		print("solidity"), (solidity)
		print("aspectRation"), (aspectRatio) 
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
			cv2.line(imgOriginal, (startX, cY), (endX, cY), (0, 0, 255), 3)
			cv2.line(imgOriginal, (cX, startY), (cX, endY), (0, 0, 255), 3)
# draw the status text on the frame
cv2.putText(imgOriginal, status, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 0, 255), 2)



#ret,thresh = cv2.threshold(gray,127,255,0)
#im2, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

#cnt = contours[4]
#cv2.drawContours(imgOriginal, [cnt], 0, (0,255,0), 3)

#cv2.imshow('img2', im2)

cv2.imshow('imgOriginal',imgOriginal)
cv2.imshow('imgThresh', imgThresh)
#cv2.imshow('imgDilate', imgDilate)
cv2.waitKey(0)
cv2.destroyAllWindows()
