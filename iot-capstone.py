##Capstone
## object detection libaries 
import requests
# pip install pillow
from PIL import Image
# pip install opencv-python
import cv2
# pip install keyboard

## import the MCP3008 for the soil moisure
from MCP3008 import MCP3008


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

#button for camera detection blynk
button_value = 0
button_emptying_fertilizer = 0
button_emptying_water = 0
#LED for the button
LED =26
#setup led
GPIO.setup(LED, GPIO.OUT)

tankfull = 4
tankempty = 14

# motor 1 inputs water
in1 = 20
in2 = 21
en1 = 16
# motor 2 inputs
in3 = 6
in4 = 13
en2 = 5


# ultrasonic 1 inputs, water tank
TRIG1 = 23
ECHO1 = 24

# ultrasonic 2 inputs, fertilizer tank
TRIG2 = 27
ECHO2 = 22

#soil moisture IO digital
#smsensor = 4

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

#soil moisture setup digital
#GPIO.setmode(GPIO.BCM)
#GPIO.setup(smsensor, GPIO.IN)

#settings for the system
#tomato #chili
#defualt
moistureLowerLimit =0
moistureUpperLimit =90

objectDetected ="chili"

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
@blynk.on("V3")
def v2_write_handler(value):
    #    global led_switch
    if int(value[0]) != 0:
        print('Empty  water tank')
        global button_emptying_water
        button_emptying_water = 1
    else:
        print('Emptying water tank stopped')
        button_emptying_water = 0
@blynk.on("V4")
def v2_write_handler(value):
    #    global led_switch
    if int(value[0]) != 0:
        print('Empty  fertilizer tank')
        global button_emptying_fertilizer
        button_emptying_fertilizer = 1
    else:
        print('Emptying fertilizer tank stopped')

        button_emptying_fertilizer = 0
        
try:
    while True:
       
        # the fertilizer periodic pump time
        fertilizerTime = time.localtime()
        blynk.run()
        print(button_value)
        
        #object detection
        if button_value==1:
            print("Processing pleasing")
            blynk.virtual_write(5, "Image processing")
            GPIO.output(LED, GPIO.HIGH)
            result = get_class_name_confidence()
            if (result["confidence"] > 0.5 and result["class_name"] == "Tomato671295"):
                blynk.virtual_write(5, "Tomato plant detected")
                blynk.virtual_write(6, "Tomato specification", "Moisture Level > 30")
                print("tomato detected")
                objectDetected ="tomato"
                GPIO.output(LED, GPIO.LOW)
                moistureLowerLimit =12
                moistureUpperLimit =95
            elif (result["confidence"] > 0.4 and result["class_name"] == "ChiliPepper677080"):
                blynk.virtual_write(5, "Chilli plant detected")
                blynk.virtual_write(6, "Chilli specification", "Moisture Level> 17")
                print("Chili pepper detected")
                objectDetected ="chili"
                GPIO.output(LED, GPIO.LOW)
                moistureLowerLimit =70
                moistureUpperLimit =80
            else:
                blynk.virtual_write(5, "Nothing detected")
                print("Nothing detected")
                GPIO.output(LED, GPIO.LOW)
        #if tomato or chili are detected then run the motors else wait for the next cycle until the button is pressed
        if objectDetected == "tomato" or objectDetected == "chili":
            print(button_emptying_water,button_emptying_fertilizer)
        
            #reading moisure
            adc = MCP3008()
            value = adc.read( channel = 0 ) # You can of course adapt the channel to be read out
            moistureInPercent =(100-(value / 1023.0 * 100));
            
            print("Percentage Moisture: %.2f" % moistureInPercent )
            print("")
            
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
            if (moistureInPercent>=moistureLowerLimit):
                print("Soil:\t\t\tMOIST")
                print("Motor:\t\t\tstop")
                GPIO.output(in1, GPIO.LOW)
                GPIO.output(in2, GPIO.LOW)
            elif (moistureInPercent<moistureLowerLimit):
                print("Soil:\t\t\tDRY")
                print("Motor:\t\t\trun")
                if (waterLevel >= tankempty):
                    GPIO.output(in1, GPIO.LOW)
                    GPIO.output(in2, GPIO.LOW)
                    # print low water level
                    blynk.virtual_write(5, "Water tank empty!")
                    print("Water level:\t\tLOW")
                else:
                    GPIO.output(in1, GPIO.HIGH)
                    GPIO.output(in2, GPIO.LOW)
                    p1.ChangeDutyCycle(30)  # speed of motor
                    print("Watering soil")

             # Motor 2 used to control the fertilizer pump, the motor will run periodically (every day at 9am)
             # the motor will stop if the fertilizerLevel is greater than 4cm (Empty fertilizer  tank2)
            #print(fertilizerTime.tm_hour,fertilizerTime.tm_min,fertilizerTime.tm_sec)
            if (fertilizerTime.tm_hour == 3 and fertilizerTime.tm_min == 35 and fertilizerTime.tm_sec<=20):
                if (fertilizerLevel >= tankempty):
                    GPIO.output(in3, GPIO.LOW)
                    GPIO.output(in4, GPIO.LOW)
                    # print low fertilizer level
                    blynk.virtual_write(5, "Fertilizer tank empty!")
                    print("Fertilizer level:\tLOW")
                    
                    #send message to user using blynk

                else:
                    GPIO.output(in3, GPIO.HIGH)
                    GPIO.output(in4, GPIO.LOW)
                    p2.ChangeDutyCycle(30)  # speed of motor
                    print("Fertilizing soil")

            else:
                GPIO.output(in3, GPIO.LOW)
                GPIO.output(in4, GPIO.LOW)
                print("stop fertilizer pump") # stop fertilizer pump
            #if emptying the water tank is pressed then the motor will run until the water tank is empty
            if button_emptying_water == 1:
                if (waterLevel >= tankempty):
                    GPIO.output(in1, GPIO.LOW)
                    GPIO.output(in2, GPIO.LOW)
                    # print low water level
                    blynk.virtual_write(5, "Water tank empty!")
                    print("low water level")
                else:
                    GPIO.output(in1, GPIO.HIGH)
                    GPIO.output(in2, GPIO.LOW)
                    p1.ChangeDutyCycle(30)  # speed of motor
            if(button_emptying_water == 0):
                GPIO.output(in1, GPIO.LOW)
                GPIO.output(in2, GPIO.LOW)
                print("stopped emptying water")
            #if emptying the fertilizer tank is pressed then the motor will run until the fertilizer tank is empty
            if button_emptying_fertilizer == 1:
                if (fertilizerLevel >= tankempty):
                    GPIO.output(in3, GPIO.LOW)
                    GPIO.output(in4, GPIO.LOW)
                    # print low fertilizer level
                    blynk.virtual_write(5, "Fertilizer tank empty!")
                    print("low fertilizer level")
                else:
                    GPIO.output(in3, GPIO.HIGH)
                    GPIO.output(in4, GPIO.LOW)
                    p2.ChangeDutyCycle(30)  # speed of motor
            if(button_emptying_fertilizer == 0):
                GPIO.output(in3, GPIO.LOW)
                GPIO.output(in4, GPIO.LOW)
                print("stopped emptying fertilizer")
            time.sleep(0.5)
        else:
            print("nothing detected")
            time.sleep(0.5)

finally:
    GPIO.cleanup()
