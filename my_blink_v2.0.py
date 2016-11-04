#DERT 2040 Vision and Python Training Materail
# my_blink.py_v2.0
#November 1, 2016
# use the circuit from "my_blink.png"
#Based on code from
#https://github.com/MicrocontrollersAndMore/Raspberry_Pi_2_and_OpenCV_3_Tutorial_Part_1/blob/master/Raspberry%20Pi%202%20%2B%20OpenCV%$
# remember to used sudo python my_blink etc etc due to the GPIO needed sudo to run

import RPi.GPIO as GPIO
import time

###################################################################################################
def main():
    #GPIO.setwarnings(False
    GPIO.setmode(GPIO.BOARD)      # use GPIO pin numbering, not physical pin numbering
    #GPIO.setwarnings(False
    led_gpio_pin = 18

    GPIO.setup(led_gpio_pin, GPIO.OUT)
    try:                          # try and except added to handle errors
                                  # Ctrl C stops in the middle making it hard to do GPIO.cleanup()
        while True:
            GPIO.output(led_gpio_pin, GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(led_gpio_pin, GPIO.LOW)
            time.sleep(0.5)
    # end while
        return
    except:                       # when Ctrl C is pressed the program jumps to teh except block
            GPIO.cleanup()        # program runs the first time after reboot but errors without this cleanup command



# end main

###################################################################################################
if __name__ == "__main__":
    main()
