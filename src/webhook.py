#camera interface connecting to API 

import time
#import requests  have to ask Abhi if we will use this 
import GPIO as GPIO
import picamera2
import os
from PIL import image #have to ask abhi if i really need this package 

BUTTON_PIN = 2  #gotta look to see what pin on raspberry pi 
API_URL = 1 #ask abhi for url

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Initialize PiCamera2
camera = picamera2.PiCamera2()
camera.resolution = (640, 480)

def capture_and_send():
    camera.capture(image.path)
    print(f"Image saved as '{image.path}'")

    #data = {
       # "device_id": "RaspberryPi_001",
    # } # have to see if were gonna use metadata 

    # Send image to API
    with open(image.path, "rb") as image_file:
        files = {"file": image_file}
        response = 1 #requests.post(API_URL, files=files) #if we use request 

    #print("API Response:", response.text)

print("button to capture and send an image")

try:
    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.LOW: 
            capture_and_send()
            time.sleep(0.5) 
except KeyboardInterrupt:
    GPIO.cleanup()
    camera.close()
