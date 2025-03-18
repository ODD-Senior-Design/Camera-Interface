import os
import time
import requests
import pigpio
import picamera2
from interface import CameraInterface
from interface import ButtonInterface

#gotta see if this is in main
class Camera:
    def __init__(self, button_pin, api_url, api_key = None):
        self.camera = CameraInterface()
        self.button = ButtonInterface(button_pin, self.capture_and_send)
        self.api_url = API_URL

    def capture_and_send(self):
        image_path = self.camera.capture_image()
        with open(image_path, "rb") as image_file:
            files = {"file": image_file}
            response = response.post(self.api_url, files = files)

        if self.uploader.upload_image(image_path) == 3 : # gotta ask how many pictures its gonna take 
            os.remove(image_path)
            print(f"Delete '{image_path}' after successful upload.")
        else: 
            print(f"error, {response.text}")

    def run(self):
       # print("Press the button to capture and send an image. Press Ctrl+C to exit.") Still don't know what the use the buttons for 
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.cleanup()

    def cleanup(self):
        print("Cleaning up")
        self.camera.close()
        self.button.close()

if __name__ == "__main__":
    API_URL = "https://api.ranga-family.com"
    BUTTON_PIN = 18  # Change GPIO pin if necessary

    app = Camera(BUTTON_PIN, API_URL) 
    app.run()

# Setup GPIO
pigpio.setmode(pigpio.BCM)
pigpio.setup(BUTTON_PIN, pigpio.IN, pull_up_down = pigpio.PUD_UP)

# Initialize PiCamera2
camera = picamera2.PiCamera2()
camera.resolution = (640, 480)
camera.configure(camera.create_still_configuration())
camera.start()

API_URL = "https://api.ranga-family.com"

def capture_and_send():
    image_path = "/home/pi/captured_image.jpg"
    camera.capture_file(image_path)
    print(f"Image saved as '{image_path}'")

    # Send image to API
    with open(image_path, "rb") as image_file:
        files = {"file": image_file}
        response = requests.post(API_URL, files=files)

    print("API Response:", response.text)

print("button to capture and send an image")

try:
    while True:
        if pigpio.input(BUTTON_PIN) == pigpio.LOW: 
            capture_and_send()
            time.sleep(0.5) 
except KeyboardInterrupt:
    pigpio.cleanup()
    camera.close()
