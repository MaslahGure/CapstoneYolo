""" 
This file contains code for raspberry pi to detect objects using the camera,
the model is tf lite model
when the model detects model it will set the settings of IoT device based on the object detected
Settings are:
    - Motor speed
    - Humidity level
-Detection will take place when button is pressed
-Default settings will be set when button is not pressed

 Will use :
    - Camera
    - Motor
    - Humidity sensor
    - Ultrasonic sensor
    - Raspberry pi
    - TF lite model
 """
 

# Importing libraries for TF lite model
import tflite_runtime.interpreter as tflite
import platform
import os
import argparse

# Importing libraries for camera
import cv2
import numpy as np
#import time

# Importing libraries for IoT device
import RPi.GPIO as GPIO
import time
import sys
#import Adafruit_DHT



# Setting up GPIO pins
# Motor
#motor inputs
in1 = 24
in2 = 23
en = 25

GPIO.setup(in1,GPIO.OUT)
GPIO.setup(in2,GPIO.OUT)
GPIO.setup(en,GPIO.OUT)
GPIO.output(in1,GPIO.LOW)
GPIO.output(in2,GPIO.LOW)


# Button
GPIO.setup(17,GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Ultrasonic sensor
TRIG = 5
ECHO = 6

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)


# Humidity sensor
""" sensor = Adafruit_DHT.DHT11
pin = 4 """
GPIO.output(TRIG, True)
time.sleep(0.00001)
GPIO.output(TRIG, False)

# Setting up motor
p=GPIO.PWM(en,1000)
p.start(25)

# Setting up TF lite model
# Get path to current working directory
CWD_PATH = os.getcwd()

# Path to .tflite file, which contains the model that is used for object detection
PATH_TO_CKPT = os.path.join(CWD_PATH,'best.tflite')

# Path to label map file
PATH_TO_LABELS = os.path.join(CWD_PATH,'labelmap.txt')

# Load the label map
with open(PATH_TO_LABELS, 'r') as f:
    labels = [line.strip() for line in f.readlines()]

# Load the Tensorflow Lite model.
interpreter = tflite.Interpreter(model_path=PATH_TO_CKPT)

# Get input and output tensors.
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Test the model on random input data.
input_shape = input_details[0]['shape']

# Setting up camera
# Camera 0 is the integrated web cam on my netbook
camera_port = 0

#Number of frames to throw away while the camera adjusts to light levels
ramp_frames = 30

# Now we can initialize the camera capture object with the cv2.VideoCapture class.
# All it needs is the index to a camera port.
camera = cv2.VideoCapture(camera_port)

# Captures a single image from the camera and returns it in PIL format
def get_image():
    # read is the easiest way to get a full image out of a VideoCapture object.
    retval, im = camera.read()
    return im

# Setting up default settings
# Default motor speed
motorSpeed = 0

# Default humidity level
humidityLevel = 0

# Default distance
distance = 0

# Default object detected
objectDetected = "None"

# Function to set motor speed
def setMotorSpeed(speed):
    # Setting motor speed
    p.ChangeDutyCycle(speed)

# Function to set humidity level
def setHumidityLevel(level):
    # Setting humidity level
    humidityLevel = level

# Function to set distance
def setDistance(dist):
    # Setting distance
    distance = dist

# Function to set object detected
def setObjectDetected(obj):
    # Setting object detected
    objectDetected = obj

# Function to set settings
def setSettings():
    # Setting motor speed
    setMotorSpeed(motorSpeed)
    # Setting humidity level
    setHumidityLevel(humidityLevel)
    # Setting distance
    setDistance(distance)
    # Setting object detected
    setObjectDetected(objectDetected)

# Function to detect object
def detectObject():
    # Setting up motor
    # Setting motor speed
    setMotorSpeed(motorSpeed)
    # Setting up humidity sensor
    # Setting humidity level
    setHumidityLevel(humidityLevel)
    # Setting up ultrasonic sensor
    # Setting distance
    setDistance(distance)
    # Setting up camera
    # Capturing image
    image = get_image()
    # Setting up TF lite model
    # Setting up input and output details
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    # Setting up input shape
    input_shape = input_details[0]['shape']
    #confidence threshold
    
    # Setting up input data
    input_data = np.expand_dims(image, axis=0)
    # Setting up output data
    output_data = np.array([[0]*91], dtype=np.float32)
    # Setting up input and output details
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.set_tensor(output_details[0]['index'], output_data)
    # Running inference
    interpreter.invoke()
    # Getting results
    output_data = interpreter.get_tensor(output_details[0]['index'])
    # Getting results
    results = np.squeeze(output_data)
    # Getting top 5 results
    top_k = results.argsort()[-5:][::-1]
    # Printing results
    
    for i in top_k:
        #if tomato
        if ((results[i] > 0.5) and (i == 0)):
            print(labels[i], results[i])
            # Setting motor speed
            motorSpeed = 100
            # Setting humidity level
            humidityLevel = 50
            # Setting distance
            distance = 10
            # Setting object detected
            objectDetected = "Tomato671295"
            print(objectDetected)
            # Setting settings
            setSettings()
        #if chilipeper
        elif ((results[i] > 0.5) and (i == 1)):
            print(labels[i], results[i])
            # Setting motor speed
            motorSpeed = 50
            # Setting humidity level
            humidityLevel = 25
            # Setting distance
            distance = 5
            # Setting object detected
            objectDetected = "ChiliPepper677080"
            print(objectDetected)
            # Setting settings
            setSettings()
        #if default
        else:
            # Setting motor speed
            motorSpeed = 0
            # Setting humidity level
            humidityLevel = 0
            # Setting distance
            distance = 0
            # Setting object detected
            objectDetected = "None"
            # Setting settings
            setSettings()

## Main loop
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

        #if button is pressed
        if(GPIO.input(17) == 0):
            print("button pressed")
            detectObject()
            # Setting motor speed
            setMotorSpeed(motorSpeed)
            # Setting humidity level
            setHumidityLevel(humidityLevel)
            # Setting distance
            setDistance(distance)
            # Setting object detected
            setObjectDetected(objectDetected)
            # Setting settings
            setSettings()
            # Printing settings
            print("motorSpeed: ", motorSpeed)
            print("humidityLevel: ", humidityLevel)
            print("distance: ", distance)
            print("objectDetected: ", objectDetected)
            

finally:
    GPIO.cleanup()

            















