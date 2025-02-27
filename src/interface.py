#buttons and camera 
#picamera works with packages but will give errors but will work on pi 
#live preview in future 

#camera outline 
import picamera2 

camera = picamera2 
camera.resolution = (660, 480) #check resolution 
camera.capture("image.jpg")
print(f"take picture")
camera.close()


#button outline 
import GPIO as GPIO
import time
import picamera2

BUTTON_PIN = 2 #have to look at pin on raspberry 
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down = GPIO.PUD_UP)

camera = picamera2
camera.resolution = (660, 480) #have to recheck resolution 

def capture_image():
    filename = "capture image.jpg"
    camera.capture(filename)
    print(f"Image saves as filename")
    print("Press button to get image")
try:
    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.LOW: 
            capture_image()
            time.sleep(0.5)  # see what time in seconds 
except KeyboardInterrupt:
    GPIO.cleanup()
    camera.close()