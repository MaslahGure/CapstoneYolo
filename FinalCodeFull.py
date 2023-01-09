##Capstone
## object detection libaries 
import requests
# pip install pillow
from PIL import Image
# pip install opencv-python
import cv2
# pip install keyboard


# extra imports native to python
import time
import io
import base64

#iot libaries
import BlynkLib
import RPi.GPIO as GPIO
from BlynkTimer import BlynkTimer
import time
import board
import adafruit_dht

dhtDevice = adafruit_dht.DHT11(board.D25)


BLYNK_AUTH_TOKEN = '_EfLT9RJX8GFVrPJ2ou6979syYz1G3Fr'
blynk = BlynkLib.Blynk(BLYNK_AUTH_TOKEN)

#button for camera detection
button_value = 0
#LED for the button
LED =26
#setup led
GPIO.setup(LED, GPIO.OUT)

tankfull = 4
tankempty = 12

# motor 1 inputs
in1 = 6
in2 = 13
en1 = 5
# motor 2 inputs
in3 = 20
in4 = 21
en2 = 16


# ultrasonic 1 inputs, water tank
TRIG1 = 23
ECHO1 = 24

# ultrasonic 2 inputs, fertilizer tank
TRIG2 = 27
ECHO2 = 22

#soil moisture IO
smsensor = 4

# motor 1 inputs setup
GPIO.setup(in1, GPIO.OUT)
GPIO.setup(in2, GPIO.OUT)
GPIO.setup(en1, GPIO.OUT)
GPIO.output(in1, GPIO.LOW)
GPIO.output(in2, GPIO.LOW)
p1 = GPIO.PWM(en1, 1000)
p1.start(25)


# motor 2 inputs setup
GPIO.setup(in3, GPIO.OUT)
GPIO.setup(in4, GPIO.OUT)
GPIO.setup(en2, GPIO.OUT)
GPIO.output(in3, GPIO.LOW)
GPIO.output(in4, GPIO.LOW)
p2 = GPIO.PWM(en2, 1000)
p2.start(25)

# ultrasonic 1 setup, water tank
GPIO.setup(TRIG1, GPIO.OUT)
GPIO.setup(ECHO1, GPIO.IN)

# ultrasonic 2 setup, water tank
GPIO.setup(TRIG2, GPIO.OUT)
GPIO.setup(ECHO2, GPIO.IN)

#soil moisture setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(smsensor, GPIO.IN)


def get_class_name_confidence():

    # Get picture from the camera using opencv skip first 30 frames
    # Get webcam interface via opencv-python
    video = cv2.VideoCapture(0)
    # skip first 30 frames and return the 31th frame
    for i in range(30):
        ret, img = video.read()
    # Resize (while maintaining the aspect ratio) to improve speed and save bandwidth
    height, width, channels = img.shape
    scale = 416 / max(height, width)
    img = cv2.resize(img, (round(scale * width), round(scale * height)))

    # change frame to jpg and save it in the folder
    cv2.imwrite("tomato_57.jpg", img)

    time.sleep(1)

    # Load image with PIL
    image =Image.open("tomato_57.jpg").convert("RGB")

    # convert to JPEG buffer
    buffer = io.BytesIO()
    image.save(buffer, quality=90, format="JPEG")

    # convert to base64 string
    img_str = base64.b64encode(buffer.getvalue())
    img_str = img_str.decode("ascii")

    # construct the url
    url = "" .join(["https://detect.roboflow.com/basbaas/12",

                    "?api_key=2Jo21qxgpkZYqXxgitc6&base64=",
                    "&name=tomato_57.jpg"]
                   )

    prediction = requests.post(url, data=img_str, headers={
                               "Content-Type": "application/x-www-form-urlencoded"})

    # prediction.plot()
    result = prediction.json()
    print(result)

   # Encode image to base64 string

    # if there is no result, then return None
    if (len(result["predictions"]) == 0):
        return {"class_name": "None", "confidence": 0}

    # pick the the prediction with the highest confidence
    for i in range(len(result["predictions"])):
        if (result["predictions"][i]["confidence"] > result["predictions"][0]["confidence"]):
            result["predictions"][0] = result["predictions"][i]

    class_name = result["predictions"][0]["class"]
    confidence = result["predictions"][0]["confidence"]
    print("The detected class is: " + class_name)
    print("confidence")
    print(confidence)

    # return result
    returnResult = {
        "class_name": class_name,
        "confidence": confidence
    }
    return returnResult
    # if the confidence is greater than 0.5 and the class is Tomato671295, then the tomato is healthy


# Create BlynkTimer Instance
timer = BlynkTimer()
@blynk.on("connected")
def blynk_connected():
    print("Raspberry Pi is connected to New Blynk")

@blynk.on("V2")
def v2_write_handler(value):
#    global led_switch
    if int(value[0]) != 0:
        print ('Scanner ON')
        global button_value
        button_value=1
        
    else:
        print('Scanner OFF')
        
        button_value=0

try:
    while True:
        print("")
        # the fertilizer periodic pump time
        fertilizerTime = time.localtime()
        blynk.run()
        print(button_value)
        
        #object detection
        if button_value==1:
            print("Processing pleasing")
            GPIO.output(LED, GPIO.HIGH)
            result = get_class_name_confidence()
            if (result["confidence"] > 0.5 and result["class_name"] == "Tomato671295"):
                print("tomato detected")
                GPIO.output(LED, GPIO.LOW)
            elif (result["confidence"] > 0.4 and result["class_name"] == "ChiliPepper677080"):
                print("Chili pepper detected")
                GPIO.output(LED, GPIO.LOW)
            else:
                print("Nothing detected")
                GPIO.output(LED, GPIO.LOW)
        
        
        
        # ultrasonic 1 water tank
        # Send a pulse to the sensor
        GPIO.output(TRIG1, True)
        time.sleep(0.00001)
        GPIO.output(TRIG1, False)
        # Measure the time it takes for the pulse to return
        while GPIO.input(ECHO1) == 0:
            water_pulse_start = time.time()
        while GPIO.input(ECHO1) == 1:
            water_pulse_end = time.time()
        # Calculate the distance based on the time it took for the pulse to return
        water_pulse_duration = water_pulse_end - water_pulse_start
        waterLevel = water_pulse_duration * 17150
        waterLevel = round(waterLevel, 2)
        print("Water level:\t\t%.2f cm" % waterLevel)

        # ultrasonic 2 fertilizer tank
        # Send a pulse to the sensor
        GPIO.output(TRIG2, True)
        time.sleep(0.00001)
        GPIO.output(TRIG2, False)
        
        # Measure the time it takes for the pulse to return
        while GPIO.input(ECHO2) == 0:
            fertilizer_pulse_start = time.time()
           
        while GPIO.input(ECHO2) == 1:
            fertilizer_pulse_end = time.time()
        # Calculate the distance based on the time it took for the pulse to return
        fertilizer_pulse_duration = fertilizer_pulse_end - fertilizer_pulse_start
        fertilizerLevel = fertilizer_pulse_duration * 17150
        fertilizerLevel = round(fertilizerLevel, 2)
        print("Fertilizer level:\t%.2f cm" % fertilizerLevel)
        
        # Motor 1 used to control the water pump, the motor will run if the soil is dry
        # the motor will stop if the soil is wet
        # the motor will stop if the waterLevel is greater than 4cm (Empty water tank1)
        if (GPIO.input(smsensor)) == 0:
            print("Soil:\t\t\tMOIST")
            print("Motor:\t\t\tstop")
            GPIO.output(in1, GPIO.LOW)
            GPIO.output(in2, GPIO.LOW)
        elif (GPIO.input(4)) == 1:
            print("Soil:\t\t\tDRY")
            print("Motor:\t\t\trun")
            if (waterLevel >= tankempty):
                GPIO.output(in1, GPIO.LOW)
                GPIO.output(in2, GPIO.LOW)
                # print low water level
                print("Water level:\t\tLOW")
            else:
                GPIO.output(in1, GPIO.HIGH)
                GPIO.output(in2, GPIO.LOW)
                p1.ChangeDutyCycle(30)  # speed of motor
                print("Watering soil")

         # Motor 2 used to control the fertilizer pump, the motor will run periodically (every day at 9am)
         # the motor will stop if the fertilizerLevel is greater than 4cm (Empty fertilizer  tank2)
        #print(fertilizerTime.tm_hour,fertilizerTime.tm_min,fertilizerTime.tm_sec)
        if (fertilizerTime.tm_hour == 16 and fertilizerTime.tm_min == 47):
            if (fertilizerLevel >= tankempty):
                GPIO.output(in3, GPIO.LOW)
                GPIO.output(in4, GPIO.LOW)
                # print low fertilizer level
                print("Fertilizer level:\tLOW")
                #send message to user using blynk

            else:
                GPIO.output(in3, GPIO.HIGH)
                GPIO.output(in4, GPIO.LOW)
                p2.ChangeDutyCycle(50)  # speed of motor
                print("Fertilizing soil")

        else:
            GPIO.output(in3, GPIO.LOW)
            GPIO.output(in4, GPIO.LOW)
            print("stop fertilizer pump") # stop fertilizer pump
        time.sleep(0.5)


finally:
    GPIO.cleanup()
