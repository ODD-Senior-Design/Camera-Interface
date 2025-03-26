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
        self.__output = FfmpegOutput( f'rtsp://{ rtsp_stream_url.strip( 'rtsp://' ) }', audio=False )
        self.__video_encoder = H264Encoder( repeat=True, iperiod=video_framerate, framerate=video_framerate )
        self.__camera.configure( self.__video_config )

    def capture_image( self, image_path: str = f'./captured_images/{ datetime.now() }.jpg' ) -> str:
        """Captures an image and saves it to the specified path."""
        self.__camera.capture_file( image_path )
        print( f"Image saved as '{ image_path }'" )
        return image_path

    def start( self ) -> str:
        self.__camera.start_recording( encoder=self.__video_encoder, output=self.__output )
        return self.__output.output_filename

    def stop(self):
        """Closes the camera."""
        self.__camera.close()

class ButtonInterface:
    def __init__( self, left_button_pin, right_button_pin, debounce_time = 0.2 ):
        self.__pi = pigpio.pi()
        self.__left_button_pin = left_button_pin
        self.__right_button_pin = right_button_pin
        self.__debounce_time = debounce_time

    # TODO: Implement actual button logic here. For now, just print the button press event.
    def __left_button_callback( self ) -> bool:
        if self.__debounce( self.__left_button_pin ):
            print( "Left button pressed" )
            return True
        return False

    # TODO: Implement actual button logic here. For now, just print the button press event.
    def __right_button_callback( self ) -> bool:
        if self.__debounce( self.__left_button_pin ):
            print( "Right button pressed" )
            return True
        return False

    def start( self ):
        self.__pi.set_mode( self.__left_button_pin, pigpio.INPUT )
        self.__pi.set_mode( self.__right_button_pin, pigpio.INPUT )
        self.__pi.callback( self.__left_button_pin, pigpio.FALLING_EDGE, self.__left_button_callback )
        self.__pi.callback( self.__right_button_pin, pigpio.FALLING_EDGE, self.__right_button_callback )

    def __debounce( self, button_pin: int ) -> bool:
        """Debounces the button input."""
        return self.__pi.wait_for_edge( button_pin, pigpio.FALLING_EDGE, wait_timeout = int( self.__debounce_time * 1000 ) )

    def stop( self ):
        self.__pi.stop()
