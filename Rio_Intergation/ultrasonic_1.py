#!/usr/bin/python
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#|R|a|s|p|b|e|r|r|y|P|i|-|S|p|y|.|c|o|.|u|k|
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#
# ultrasonic_1.py
# Measure distance using an ultrasonic module
# in a loop.
#
# Author : Matt Hawkins
# Date   : 28/01/2013

# Modified Feb 22, 2017 David Atkinson Dunlap Eagles Robotics Team #2040
# For use with MaxBotix HRLV-MaxSonar EZ Series Ultrasocic Range Finder
# Read the DATA sheet
#  http://www.maxbotix.com/documents/HRLV-MaxSonar-EZ_Datasheet.pdf

# -----------------------
# Import required Python libraries
# -----------------------

import time
import RPi.GPIO as GPIO

# -----------------------
# Define some functions
# -----------------------

def measure():
  # This function measures a distance
  GPIO.output(GPIO_TRIGGER, True)
  #minumum time for trigger is 20 micro seconds. 
  time.sleep(0.000020)
  GPIO.output(GPIO_TRIGGER, False)
  start = time.time()
  while GPIO.input(GPIO_ECHO)==0:
      start = time.time()
    
  while GPIO.input(GPIO_ECHO)==1:
    stop = time.time()
    
  elapsed = stop-start
# from spec sheet...1uSec = 1 mm. Pi keeps track of time is seconds. 
# So multiple elapsed time by 1,000,000 to convert to mm.
# To convert to inches. Divide 1,000,000 by 25.4 
  distance = (elapsed *(1000000/25.4)) #do not have to divide by 2 for this sensor
#  print("Elapsed Time (s):" , elapsed) # to check that time is working right	  
# distance is in inches.

  return distance

def measure_average():
  # This function takes 2 measurements and
  # returns the average. 
  # changes to 2 points to speed up
  distance1=measure()
  time.sleep(0.005)
  distance2=measure()
  time.sleep(0.005)
  #distance3=measure()
  distance = distance1 + distance2 
  distance = distance / 2
  return distance

# -----------------------
# Main Script
# -----------------------

# Use BCM GPIO references
# instead of physical pin numbers
GPIO.setmode(GPIO.BCM)

# Define GPIO to use on Pi. Make sure to use the correct pin out chart for your particular PI model
GPIO_TRIGGER = 24
GPIO_ECHO    = 21

print "Ultrasonic Measurement (inches)"

# Set pins as output and input
GPIO.setup(GPIO_TRIGGER,GPIO.OUT)  # Trigger
GPIO.setup(GPIO_ECHO,GPIO.IN)      # Echo

# Set trigger to False (Low)
GPIO.output(GPIO_TRIGGER, False)

# Wrap main content in a try block so we can
# catch the user pressing CTRL-C and run the
# GPIO cleanup function. This will also prevent
# the user seeing lots of unnecessary error
# messages.
try:

  while True:

    distance = measure_average()
    print "Distance : %.1f" % distance
    time.sleep(.005)

except KeyboardInterrupt:
  # User pressed CTRL-C
  # Reset GPIO settings
  GPIO.cleanup()
