## 

import time
import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BOARD)
GPIO.setup(29, GPIO.IN)

try:
    while True:
        if(GPIO.input(29) )== 0:
            print("print wet")
        elif(GPIO.input(29) )== 1:
            print("print dry")
        time.sleep(0.5)

finally:
    GPIO.cleanup()
