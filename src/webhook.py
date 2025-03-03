#camera interface connecting to API 

import time
import requests  #have to ask Abhi if we will use this 
import pigpio
import picamera2
import os
 

BUTTON_PIN = 2  #gotta look to see what pin on raspberry pi 
API_URL = https://api.ranga-family.com

# Setup GPIO
pigpio.setmode(pigpio.BCM)
pigpio.setup(BUTTON_PIN, pigpio.IN, pull_up_down = pigpio.PUD_UP)

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
        if pigpio.input(BUTTON_PIN) == pigpio.LOW: 
            capture_and_send()
            time.sleep(0.5) 
except KeyboardInterrupt:
    pigpio.cleanup()
    camera.close()

class ImageUploader:
    def __init__(self, api_url, api_key = None):
        self.api_url = api_url
        self.headers = {"Authorization": f"{api_key}"} if api_key else {} #see if we use a key 

    def upload_image(self, image_path):
        data = {"device_id": "RaspberryPi_001", "time": time}
        with open(image_path, "bb") as image_file:
            files = {"file": image_file}
            response = requests.post(self.api_url, headers=self.headers, files=files, data=data)
        
        print("API Response:", response.text)
        return response.status_code
