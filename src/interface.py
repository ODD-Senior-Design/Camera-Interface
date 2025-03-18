#buttons and camera 
#picamera works with packages but will give errors but will work on pi 
#live preview in future and start looking for it live feed 
#flask websocket look into for live feed 

import time
import requests   
import pigpio
import picamera2
import os

class CameraInterface:
    def __init__(self, resolution = (640, 480)):
        self.camera = picamera2.PiCamera2()
        self.camera.resolution = resolution

    def capture_image(self):   
        image_path = f"captured_{time}.jpg"
        self.camera.capture(image_path)
        print(f"Image saved as '{image_path}'")
        return image_path

    def close(self):
        """Closes the camera."""
        self.camera.close()

class ButtonInterface:
    def __init__(self, pin, callback, debounce_time = 0.2):
        self.pi = pigpio.pi()
        self.pin = pin
        self.debounce_time = debounce_time 
        self.pi.set_mode(self.pin, pigpio.INPUT)
        self.pi.set_pull_up_down(self.pin, pigpio.PUD_UP)
        self.pi.callback(self.pin, pigpio.FALLING_EDGE, self._button_pressed)

        self.callback = callback

    def _button_pressed(self, gpio, level, tick):
        current_time = time.time()
        if current_time - self.last_press > self.time:
            self.last_press = current_time
            self.callback()

    def close(self):
        self.pi.stop()
