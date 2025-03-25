#buttons and camera
#picamera works with packages but will give errors but will work on pi
#live preview in future and start looking for it live feed
#flask websocket look into for live feed

import pigpio
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput

from datetime import datetime

from typing import Tuple

class CameraInterface:
    def __init__( self, rtsp_stream_url: str, resolution: Tuple[ int, int ] = ( 640, 480 ), video_framerate: int = 30 ):
        self.__camera: Picamera2 = Picamera2()
        self.__video_config = self.__camera.create_video_configuration( main={ "size": resolution, "format": "RGB888"}, controls={ 'FrameRate': video_framerate } )
        self.__output = FfmpegOutput( f'rtsp://{ rtsp_stream_url }', audio=False )
        self.__video_encoder = H264Encoder( repeat=True, iperiod=30, framerate=video_framerate )
        self.__camera.configure( self.__video_config )

    def capture_image( self, image_path: str = f'./captured_images/{ datetime.now() }.jpg' ) -> str:
        """Captures an image and saves it to the specified path."""
        self.__camera.capture_file( image_path )
        print( f"Image saved as '{ image_path }'" )
        return image_path

    def start( self ) -> str:
        self.__camera.start_recording( encoder=self.__video_encoder, output=self.__output )
        return self.__output.output_filename

    def close(self):
        """Closes the camera."""
        self.__camera.close()

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
