import cv2
import numpy as np
import math
import os
import socket

os.system('v4l2-ctl --set-ctrl=exposure_auto=1')
os.system('v4l2-ctl --set-ctrl=exposure_absolute=5')
os.system('v4l2-ctl --set-ctrl=brightness=30')

adjustYaw = 1.0
adjustDistance = 575.0

UDP_IP = '10.20.40.2'

UDP_PORT = 5805
clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

cameraWidth = 640
cameraHeight = 360
horizontalAspect = 16
verticalAspect = 9
diagonalAspect = math.hypot(horizontalAspect, verticalAspect)
diagonalView = math.radians(68.5)
horizontalView = math.atan(math.tan(diagonalView / 2) * (horizontalAspect / diagonalAspect)) * 2
verticalView = math.atan(math.tan(diagonalView / 2) * (verticalAspect / diagonalAspect)) * 2
horizontalLength = cameraWidth / (2 * math.tan((horizontalView / 2)))
verticalLength = cameraHeight / (2 * math.tan((verticalView / 2)))

cy = 1
imgy = 0

def Contours(img, mask):
	_, contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_TC89_KCOS)
	rows, columns, _ = img.shape
	imgx = (rows / 2) - 0.5
	imgy = (columns / 2) - 0.5
	if len(contours) != 0:
		img = Targets(contours, img, imgx, imgy)
	return img

def Targets(contours, img, imgx, imgy):
	rows, columns, channels = img.shape
	tape = []
	if len(contours) >= 2:
		cntSorted = sorted(contours, key=lambda x: cv2.contourArea(x), reverse=True)
		cntMax = []
		for cnt in cntSorted:
			M = cv2.moments(cnt)
			hull = cv2.convexHull(cnt)
			cntArea = cv2.contourArea(cnt)
			hullArea = cv2.contourArea(hull)
			if (Check(cntArea, hullArea)):
				if M['m00'] != 0:
					cx = int(M['m10'] / M['m00'])
					cy = int(M['m01'] / M['m00'])
				else:
					cx, cy = 0, 0
				if(len(cntMax) < 10):
					rotation = Rotation(img, cnt)
					rect = cv2.minAreaRect(cnt)
					box = cv2.boxPoints(rect)
					box = np.int0(box)
					cv2.drawContours(img, [box], 0, (0, 255, 0), 3)
					cv2.line(img, (cx, rows), (cx, 0), (255, 255, 255))
					cv2.circle(img, (cx, cy), 6, (255, 255, 255))
					cv2.drawContours(img, [cnt], 0, (0, 255, 0), 1)
					(x, y), radius = cv2.minEnclosingCircle(cnt)
					center = (int(x), int(y))
					radius = int(radius)
					rx, ry, rw, rh = cv2.boundingRect(cnt)
					boundingRect = cv2.boundingRect(cnt)
					cv2.rectangle(img, (rx, ry), (rx + rw, ry + rh), (0, 255, 0), 1)
					cv2.circle(img, center, radius, (0, 255, 0), 1)
					if any([cx, cy, rotation, cnt]) not in cntMax:
						cntMax.append([cx, cy, rotation, cnt])
                cntMax = sorted(cntMax, key=lambda x: x[0])
                for i in range(len(cntMax) - 1):
                        tilt1 = cntMax[i][2]
                        tilt2 = cntMax[i + 1][2]
                        cx1 = cntMax[i][0]
                        cx2 = cntMax[i + 1][0]
                        cy1 = cntMax[i][1]
                        cy2 = cntMax[i + 1][1]
                        tapeArea = []
                        if (np.sign(tilt1) != np.sign(tilt2)):
                                tapeCenter = math.floor((cx1 + cx2) / 2)
                                if (tilt1 > 0):
                                        if (cx1 > cx2):
                                                continue
                                if (tilt2 > 0):
                                        if (cx2 > cx1):
                                                continue
                                tapeRect = cv2.minAreaRect(cntMax[i][3])
				tapeBox = cv2.boxPoints(tapeRect)
                                tapeLength1 = math.fabs(math.hypot(tapeBox[0][0] - tapeBox[1][0], tapeBox[0][1] - tapeBox[1][1]))
                                tapeLength2 = math.fabs(math.hypot(tapeBox[0][0] - tapeBox[3][0], tapeBox[0][1] - tapeBox[3][1]))
                                if tapeLength1 > tapeLength2:
                                        tapeLength = tapeLength1
                                else:
                                        tapeLength = tapeLength2
                                tapeDistance = (adjustDistance * 5.5) / tapeLength - 26.0
				tapeYaw = (adjustYaw * math.degrees(math.atan((tapeCenter - imgy) / horizontalLength))) - (5.145 * (0.960 ** tapeDistance))
#				tapeWeight = (tapeDistance / 8.75) + math.fabs(tapeYaw)
				tapeWeight = tapeDistance
				if [tapeCenter, tapeYaw, tapeDistance, tapeWeight] not in tape:
					tape.append([tapeCenter, tapeYaw, tapeDistance, tapeWeight])
	if (len(tape) > 0):
		tape = sorted(tape, key=lambda x: x[3])
		tapeFinal = tape[0]
		cv2.line(img, (int(tapeFinal[0]), rows), (int(tapeFinal[0]), 0), (255, 0, 0), 2)
		tapeMessage = ['%.3f'%(tapeFinal[0]), '%.3f'%(tapeFinal[1]), '%.3f'%(tapeFinal[2])]
		print tapeMessage
		clientSock.sendto(str(tapeMessage), (UDP_IP, UDP_PORT))
	return img

def Rotation(img, cnt):
	try:
		ellipse = cv2.fitEllipse(cnt)
		ellipseCenter = ellipse[0]
		ellipseHeight = elipse[1][1]
		ellipseWidth = ellipse[1][0]
		rotation = ellipse[2]
		if ellipseWidth > ellipseHeight:
			rotation = -1 * (rotation - 90)
		if rotation > 90:
			rotation = -1 * (rotation - 180)
		cv2.ellipse(img, ellipse, (0, 255, 0), 3)
		if elipseHeight > ellipseWidth:
			shortest = ellipseWidth
		else:
			shortest = ellipseHeight
		return rotation
	except:
		rect = cv2.minAreaRect(cnt)
		box = cv2.boxPoints(rect)
		box = np.int0(box)
		ellipseCenter = rect[0]
		ellipseHeight = rect[1][1]
		ellipseWidth = rect[1][0]
		rotation = rect[2]
		if ellipseWidth > ellipseHeight:
			rotation = -1 * (rotation - 90)
		if rotation > 90:
			rotation = -1 * (rotation - 180)
		return rotation

def Check(cntArea, hullArea):
	return (cntArea > (cameraWidth / 6))

capture = cv2.VideoCapture(-1)
while (capture.isOpened()):
	ret, img = capture.read()
	if ret == True:
		blur = cv2.medianBlur(img, 5)
		hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
		mask = cv2.inRange(hsv, np.uint8([55, 150, 100]), np.uint8([100, 255, 255]))
		Contours(img, mask)
#		cv2.imshow('img', img)
#		if cv2.waitKey(25) & 0xFF == ord('q'):
#			break
capture.release()
cv2.destroyAllWindows()

