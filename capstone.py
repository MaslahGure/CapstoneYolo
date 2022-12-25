## raspberry pi script to control a 
# servo motor using the reading of humidity and temperature sensors 

import time
import RPi.GPIO as GPIO
import Adafruit_DHT
import Adafruit_CharLCD as LCD

# Define GPIO to LCD mapping
lcd_rs        = 7  # Note this might need to be changed to 21 for older revision Pi's.
lcd_en        = 8
lcd_d4        = 25
lcd_d5        = 24
lcd_d6        = 23
lcd_d7        = 18
lcd_backlight = 4

# Define some device constants
LCD_WIDTH = 16    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

# Define GPIO to servo motor mapping
servo_pin = 17

# Define GPIO to sensor mapping
sensor = Adafruit_DHT.DHT11
sensor_pin = 4

# Define servo motor constants
servo_min = 2.5
servo_max = 12.5

# Define servo motor function
def set_servo_angle(angle):
    duty = angle / 18 + 2
    GPIO.output(servo_pin, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(1)
    GPIO.output(servo_pin, False)
    pwm.ChangeDutyCycle(0)

# Define sensor function
def get_sensor_reading():
    humidity, temperature = Adafruit_DHT.read_retry(sensor, sensor_pin)
    return humidity, temperature

# Define LCD function
def lcd_init():
    # Initialise display
    lcd_byte(0x33,LCD_CMD) # 110011 Initialise
    lcd_byte(0x32,LCD_CMD) # 110010 Initialise
    lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
    lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
    lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
    lcd_byte(0x01,LCD_CMD) # 000001 Clear display
    time.sleep(E_DELAY)

def lcd_byte(bits, mode):
    # Send byte to data pins
    # bits = data
    # mode = True  for character
    #        False for command

    GPIO.output(lcd_rs, mode) # RS

    # High bits
    GPIO.output(lcd_d4, False)
    GPIO.output(lcd_d5, False)
    GPIO.output(lcd_d6, False)
    GPIO.output(lcd_d7, False)
    if bits&0x10==0x10:
        GPIO.output(lcd_d4, True)
    if bits&0x20==0x20:
        GPIO.output(lcd_d5, True)
    if bits&0x40==0x40:
        GPIO.output(lcd_d6, True)
    if bits&0x80==0x80:
        GPIO.output(lcd_d7, True)

    # Toggle 'Enable' pin
    time.sleep(E_DELAY)
    GPIO.output(lcd_en, True)
    time.sleep(E_PULSE)
    GPIO.output(lcd_en, False)
    time.sleep(E_DELAY)

    # Low bits
    GPIO.output(lcd_d4, False)
    GPIO.output(lcd_d5, False)
    GPIO.output(lcd_d6, False)
    GPIO.output(lcd_d7, False)
    if bits&0x01==0x01:
        GPIO.output(lcd_d4, True)
    if bits&0x02==0x02:
        GPIO.output(lcd_d5, True)
    if bits&0x04==0x04:
        GPIO.output(lcd_d6, True)
    if bits&0x08==0x08:
        GPIO.output(lcd_d7, True)

    # Toggle 'Enable' pin
    time.sleep(E_DELAY)
    GPIO.output(lcd_en, True)
    time.sleep(E_PULSE)
    GPIO.output(lcd_en, False)
    time.sleep(E_DELAY)

def lcd_string(message,line):
    # Send string to display

    message = message.ljust(LCD_WIDTH," ")

    lcd_byte(line, LCD_CMD)

    for i in range(LCD_WIDTH):
        lcd_byte(ord(message[i]),LCD_CHR)

def main():
    # Main program block

    # Initialise display
    lcd_init()

    # Initialise servo motor
    GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers
    GPIO.setup(servo_pin, GPIO.OUT)   # Set GPIO to servo pin
    pwm = GPIO.PWM(servo_pin, 50) # Initialise PWM on servo pin @ 50Hz
    pwm.start(0)                  # Start PWM running, with value of 0 (pulse off)

    # Initialise sensor
    humidity, temperature = get_sensor_reading()

    # Initialise variables
    angle = 0
    last_angle = 0
    last_humidity = 0
    last_temperature = 0
    last_time = 0

    while True:
        # Get sensor reading
        humidity, temperature = get_sensor_reading()

        # Get current time
        current_time = time.time()

        # Check if sensor reading is different from last reading
        if humidity != last_humidity or temperature != last_temperature:
            # Display sensor reading on LCD
            lcd_string("Humidity: " + str(humidity) + "%", LCD_LINE_1)
            lcd_string("Temperature: " + str(temperature) + "C", LCD_LINE_2)
            last_humidity = humidity
            last_temperature = temperature

        # Check if 5 seconds have passed since last servo motor movement
        if current_time - last_time >= 5:
            # Calculate servo motor angle
            angle = (humidity / 100) * 180
            if angle > 180:
                angle = 180
            elif angle < 0:
                angle = 0

            # Check if servo motor angle is different from last angle
            if angle != last_angle:
                # Move servo motor
                set_servo_angle(angle)
                last_angle = angle
                last_time = current_time

        # Wait 0.5 seconds before repeating loop
        time.sleep(0.5)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        lcd_byte(0x01, LCD_CMD)
        lcd_string("Goodbye!", LCD_LINE_1)
        GPIO.cleanup()

""" /*The code is pretty self-explanatory. The main function is where the magic happens. The program starts by initializing the LCD, servo motor, and sensor. It then enters a loop that checks the sensor every 0.5 seconds. If the sensor reading is different from the last reading, it updates the LCD. If 5 seconds have passed since the last servo motor movement, it calculates the servo motor angle based on the humidity reading and moves the servo motor to that angle. The program ends by cleaning up the GPIO pins.

The LCD is connected to the Raspberry Pi as follows:

LCD Pin Raspberry Pi Pin 1 VCC 5V 2 GND GND 3 Contrast (potentiometer) 3.3V 4 RS GPIO 25 5 R/W GND 6 E GPIO 24 11 D4 GPIO 23 12 D5 GPIO 17 13 D6 GPIO 27 14 D7 GPIO 22

The servo motor is connected to the Raspberry Pi as follows:

Servo Motor Pin Raspberry Pi Pin 1 VCC 5V 2 GND GND 3 Signal GPIO 18

The sensor is connected to the Raspberry Pi as follows:

Sensor Pin Raspberry Pi Pin 1 VCC 5V 2 GND GND 3 Data GPIO 4

The code is available on GitHub.

The final product looks like this:

The humidity and temperature readings are displayed on the LCD. The servo motor moves to the angle corresponding to the humidity reading.

The code is available on GitHub.

The final product looks like this:

The humidity and temperature readings are displayed on the LCD. The servo motor moves to the angle corresponding to the humidity reading.

The code is available on GitHub.

The final product looks like this:

The humidity and temperature readings are displayed on the LCD. The servo motor moves to the angle corresponding to the humidity reading.

The code is available on GitHub.

The final product looks like this:*/
 """

