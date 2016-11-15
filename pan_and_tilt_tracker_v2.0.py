# pan_and_tilt_tracker_v2.0.py
# if using Putty and X ming type this on the command line first    xauth extract - $DISPLAY | sudo xauth merge -
# then enter "sudo python pan_and_tilt............

# to run this program, type:
# sudo python pan_and_tilt_tracker.py headed          (GUI)
# sudo python pan_and_tilt_tracker.py headless        (no GUI (for embedded use))

# this program pans/tilts two servos so a mounted webcam tracks a red ball

# use the circuit from "pan_and_tilt_tracker.png"
import time
import RPi.GPIO as GPIO
import cv2
import numpy as np
import os
import sys
from operator import itemgetter

###################################################################################################
def main():
    headed_or_headless = ""

    if len(sys.argv) == 2 and str(sys.argv[1]) == "headed":
        headed_or_headless = "headed"
        print ("entering headed mode")
    elif len(sys.argv) == 2 and str(sys.argv[1]) == "headless":
        headed_or_headless = "headless"
        print ("entering headless mode")
    else:
        print ("\nprogram usage:\n")
        print ("for headed mode (GUI interface) @command prompt type: sudo python pan_and_tilt_tracker.py headed\n")
        print ("for headless mode (no GUI interface, i.e. embedded mode) @ command prompt type: sudo python pan_and_tilt_tracker.py headless\n")
        return
    # end if else

    GPIO.setmode(GPIO.BCM)              # use GPIO pin numbering, not physical pin numbering

    led_gpio_pin = 18
    pan_gpio_pin = 24
    tilt_gpio_pin = 25

    pwmFrequency = 100                 # frequency in Hz
    pwmInitialDutyCycle = 14           # initial duty cycle in %

    GPIO.setup(led_gpio_pin, GPIO.OUT)
    GPIO.setup(pan_gpio_pin, GPIO.OUT)
    GPIO.setup(tilt_gpio_pin, GPIO.OUT)

    pwmPanObject = GPIO.PWM(pan_gpio_pin, pwmFrequency)
    pwmTiltObject = GPIO.PWM(tilt_gpio_pin, pwmFrequency)

    pwmPanObject.start(pwmInitialDutyCycle)
    pwmTiltObject.start(pwmInitialDutyCycle)

    capWebcam = cv2.VideoCapture(0)                     # declare a VideoCapture object and associate to webcam, 0 => use 1st webcam

    print (("default resolution = ") + str(capWebcam.get(cv2.CAP_PROP_FRAME_WIDTH)) + ("x") + str(capWebcam.get(cv2.CAP_PROP_FRAME_HEIGHT)))

    capWebcam.set(cv2.CAP_PROP_FRAME_WIDTH, 320.0)
    capWebcam.set(cv2.CAP_PROP_FRAME_HEIGHT, 240.0)

    print (("updated resolution = ") + str(capWebcam.get(cv2.CAP_PROP_FRAME_WIDTH)) + ("x") + str(capWebcam.get(cv2.CAP_PROP_FRAME_HEIGHT)))

    if capWebcam.isOpened() == False:                           # check if VideoCapture object was associated to webcam successfully
        print ("error: capWebcam not accessed successfully\n\n")          # if not, print error message to std out
        os.system("pause")                                              # pause until user presses a key so user can see error message
        return                                                          # and exit function (which exits program)
    # end if

    intXFrameCenter = int(float(capWebcam.get(cv2.CAP_PROP_FRAME_WIDTH)) / 2.0)
    intYFrameCenter = int(float(capWebcam.get(cv2.CAP_PROP_FRAME_WIDTH)) / 2.0)

    panServoPosition = int(90)           # pan servo position in degrees
    tiltServoPosition = int(90)          # tilt servo position in degrees

    updateServoMotorPositions(pwmPanObject, panServoPosition, pwmTiltObject, tiltServoPosition)

    while cv2.waitKey(1) != 27 and capWebcam.isOpened():                # until the Esc key is pressed or webcam connection is lost
        blnFrameReadSuccessfully, imgOriginal = capWebcam.read()            # read next frame

        if not blnFrameReadSuccessfully or imgOriginal is None:             # if frame was not read successfully
            print ("error: frame not read from webcam\n")                     # print error message to std out
            os.system("pause")                                              # pause until user presses a key so user can see error message
            break                                                           # exit while loop (which exits program)
        # end if

        imgHSV = cv2.cvtColor(imgOriginal, cv2.COLOR_BGR2HSV)

        imgThreshLow = cv2.inRange(imgHSV, np.array([0, 135, 135]), np.array([19, 255, 255]))
        imgThreshHigh = cv2.inRange(imgHSV, np.array([168, 135, 135]), np.array([179, 255, 255]))

        imgThresh = cv2.add(imgThreshLow, imgThreshHigh)

        imgThresh = cv2.GaussianBlur(imgThresh, (3, 3), 2)

        imgThresh = cv2.dilate(imgThresh, np.ones((5,5),np.uint8))
        imgThresh = cv2.erode(imgThresh, np.ones((5,5),np.uint8))

        intRows, intColumns = imgThresh.shape

        circles = cv2.HoughCircles(imgThresh, cv2.HOUGH_GRADIENT, 3, intRows / 4)      # fill variable circles with all circles in the processed image

        GPIO.output(led_gpio_pin, GPIO.LOW)

        if circles is not None:                     # this line is necessary to keep program from crashing on next line if no circles were found
            GPIO.output(led_gpio_pin, GPIO.HIGH)

            sortedCircles = sorted(circles[0], key = itemgetter(2), reverse = True)

            largestCircle = sortedCircles[0]

            x, y, radius = largestCircle                                                                       # break out x, y, and radius
            print (("ball position x = ") + str(x) + (", y = ") + str(y) + (", radius = ") + str(radius))       # print ball position and radius
            Err_X = x - intXFrameCenter     # right side of screen in zero. Positive error  means move camera to the right-a smaller angle
            Err_Y = intYFrameCenter - y     # top of the screen is zero Y. if Err_Y is positive, camera needs to rotate to a smaller angle
            Deadband_X = 15            # deadband prevents servo from dithering back and forth near zero
            Deadband_Y = 30
            print (("Pan error from center= ") + str(Err_X))
            print (("Tilt  error from center= ") + str(Err_Y))

            if Err_X > Deadband_X and panServoPosition >= 2: 
                panServoPosition = panServoPosition - 1          # 90 degress points camera at 12 o'clock (straight ahead) 0 deg is 3 o'clock
            elif Err_X < -Deadband_X and panServoPosition >= 178:
                panServoPosition = panServoPosition + 1
            
            # end if else

            if Err_Y < Deadband_Y and tiltServoPosition <= 133:                     # 90 degress is level. smaller angles poin the camera up.
                tiltServoPosition = tiltServoPosition + 1
            elif Err_Y > Deadband_Y and tiltServoPosition >= 62:
                tiltServoPosition = tiltServoPosition - 1
            # end if else

            updateServoMotorPositions(pwmPanObject, panServoPosition, pwmTiltObject, tiltServoPosition)
            time.sleep(.3)                                       # lets the servo catch up but it delys the whole program
            if headed_or_headless == "headed":
                cv2.circle(imgOriginal, (x, y), 3, (0, 255, 0), -1)           # draw small green circle at center of detected object
                cv2.circle(imgOriginal, (x, y), radius, (0, 0, 255), 3)                     # draw red circle around the detected object
            # end if

        # end if

        if headed_or_headless == "headed":
            cv2.imshow("imgOriginal", imgOriginal)                 # show windows
            cv2.imshow("imgThresh", imgThresh)                    # comment out to save bandwidth in headed mode
        # end if
    # end while

    cv2.destroyAllWindows()                     # remove windows from memory
    GPIO.cleanup()				# resets GPIO for next run to avoid errors
    return
# end main

###################################################################################################
def updateServoMotorPositions(pwmPanObject, panServoPosition, pwmTiltObject, tiltServoPosition):
    panDutyCycle = ((float(panServoPosition) * 0.01) + 0.5) * 10
    tiltDutyCycle = ((float(tiltServoPosition) * 0.01) + 0.5) * 10

    pwmPanObject.ChangeDutyCycle(panDutyCycle)
    pwmTiltObject.ChangeDutyCycle(tiltDutyCycle)
# end function

###################################################################################################
if __name__ == "__main__":
    main()



