import cv2
import numpy as np
import os
import socket

adjustDistance = 600.0
adjustYaw = 1
focalLength = 600.0

os.system('v4l2-ctl --set-ctrl brightness=80')
os.system('v4l2-ctl --set-ctrl exposure_auto=1')
os.system('v4l2-ctl --set-ctrl exposure_absolute=1000')

UDP_IP = '10.20.40.2'
UDP_PORT = 2040

capture = cv2.VideoCapture(-1)
while(capture.isOpened()):
	ret, frame = capture.read()
	_, columns, _ = frame.shape
	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
	mask = cv2.inRange(hsv, np.array([0, 105, 105]), np.array([150, 255, 255]))
	mask = cv2.erode(mask, None, iterations = 2)
	mask = cv2.erode(mask, None, iterations = 2)
	_, contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
	if len(contours) > 0:
		cntMax = max(contours, key=cv2.contourArea)
		((x, y), r) = cv2.minEnclosingCircle(cntMax)
		M = cv2.moments(cntMax)
		cntCenter = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))
		if r > 40:
			distance = adjustDistance * 6.5 / r
			yaw = adjustYaw * np.degrees(np.arctan(((columns / 2) - x) / focalLength))
			message = ['%.3f'%(distance), '%.3f'%(yaw)]
			sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			sock.sendto(str(message), (UDP_IP, UDP_PORT))
capture.release()
cv2.destroyAllWindows()
