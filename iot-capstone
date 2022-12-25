## 

import time
import RPi.GPIO as GPIO
#motor inputs
in1 = 24
in2 = 23
en = 25


GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN)
#motor inputs
GPIO.setup(in1,GPIO.OUT)
GPIO.setup(in2,GPIO.OUT)
GPIO.setup(en,GPIO.OUT)
GPIO.output(in1,GPIO.LOW)
GPIO.output(in2,GPIO.LOW)
p=GPIO.PWM(en,1000)
p.start(25)

#ultasonic 
TRIG = 5
ECHO = 6

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)


try:
    while True:
        ## ultrasonic
        # Send a pulse to the sensor
        GPIO.output(TRIG, True)
        time.sleep(0.00001)
        GPIO.output(TRIG, False)
        # Measure the time it takes for the pulse to return
        while GPIO.input(ECHO) == 0:
            pulse_start = time.time()
        while GPIO.input(ECHO) == 1:
            pulse_end = time.time()
        # Calculate the distance based on the time it took for the pulse to return
        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150
        distance = round(distance, 2)

        print("Distance: %.2f cm" % distance)
        
        
        if(GPIO.input(4) )== 0:
            print("print wet")
            print("stop")
            GPIO.output(in1,GPIO.LOW)
            GPIO.output(in2,GPIO.LOW)
        elif(GPIO.input(4) )== 1:
            print("print dry")
            print("run")
            if(distance >= 4):
               GPIO.output(in1,GPIO.LOW)
               GPIO.output(in2,GPIO.LOW)
            else:
                GPIO.output(in1,GPIO.HIGH)
                GPIO.output(in2,GPIO.LOW)
                p.ChangeDutyCycle(30)
                print("forward")
        time.sleep(0.5)

finally:
    GPIO.cleanup()
