import os
import time
import pigpio
import picamera2
from interface import CameraInterface
from interface import ButtonInterface
from webhook import ImageUploader

#gotta see if this is in main
class Camera:
    def __init__(self, button_pin, api_url, api_key = None):
        self.camera = CameraInterface()
        self.uploader = ImageUploader(api_url, api_key)
        self.button = ButtonInterface(button_pin, self.capture_and_send)

    def capture_and_send(self):
        image_path = self.camera.capture_image()
        if self.uploader.upload_image(image_path) == 3 : # gotta ask how many pictures its gonna take 
            os.remove(image_path)
            print(f"Delete '{image_path}' after successful upload.")

    def run(self):
        #print("Press the button to capture and send an image. Press Ctrl+C to exit.") gonne see how were gonna do that 
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
    API_URL = https://api.ranga-family.com
    BUTTON_PIN = 18  # Change GPIO pin if necessary
    #API_KEY = "YOUR_API_KEY"  ask abhi if we have a key 

    app = Camera(BUTTON_PIN, API_URL) #API_KEY)
    app.run()