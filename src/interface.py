import pigpio
import cv2
from numpy import ndarray
import threading
# from picamera2 import Picamera2
# from picamera2.encoders import H264Encoder
# from picamera2.outputs import FfmpegOutput

from datetime import datetime
from typing import Tuple, Union, Optional

class CameraInterface:

    def __init__( self, rtsp_stream_url: str, resolution: Tuple[ int, int ] = ( 640, 480 ), video_framerate: int = 30, camera_device: Union[ str, int ] = 0, stream_thread_timeout: float = 10 ) -> None:
        self.__camera: cv2 = cv2.VideoCapture( camera_device, cv2.CAPDSHOW )
        if not self.__camera.isOpened():
            raise ValueError( f"Failed to open camera '{ camera_device }'" )

        self.__camera.set( cv2.CAP_PROP_FRAME_WIDTH, resolution[ 0 ] )
        self.__camera.set( cv2.CAP_PROP_FRAME_HEIGHT, resolution[ 1 ] )
        self.__camera.set( cv2.CAP_PROP_FPS, video_framerate )

        self.__last_frame: Optional[ ndarray ] = None
        self.__stream_thread = threading.Thread( target = self.__stream_thread_handler )
        self.__stream_thread_timeout = stream_thread_timeout

    def capture_image( self, image_path: str = f'./captured_images/{ datetime.now() }.jpg' ) -> Optional[ str ]:
        if not self.__last_frame:
            print( 'Please start camera first' )
            return None

        img = cv2.cvtColor( self.__last_frame, cv2.COLOR_BGR2RGB )
        error = cv2.imwrite( image_path, img )
        if not error:
            print( f"Failed to save image at '{ image_path }'" )
            return None
        return image_path

    def get_last_frame( self ) -> Optional[ ndarray ]:
        return self.__last_frame

    def __stream_thread_handler( self ) -> None:
        valid, frame = self.__camera.read()
        while valid and self.__camera.isOpened():
            self.__last_frame = frame
            valid, frame = self.__camera.read()

        self.__last_frame = None

    def start( self ) -> str:
        self.__stream_thread.start()

    def stop( self ):
        self.__camera.release()
        self.__stream_thread.join( timeout=self.__stream_thread_timeout )

class ButtonInterface:
    """Provides an interface to interact with physical buttons.

    This class handles button press detection and debouncing using the pigpio library.
    It provides methods to start and stop listening for button presses.
    """
    def __init__( self, left_button_pin, right_button_pin, debounce_time = 0.2 ):
        """Initializes the ButtonInterface with the specified button pins and debounce time.

        Args:
            left_button_pin: The GPIO pin connected to the left button.
            right_button_pin: The GPIO pin connected to the right button.
            debounce_time (float): The debounce time in seconds. Defaults to 0.2.
        """
        self.__pi = pigpio.pi()
        self.__left_button_pin = left_button_pin
        self.__right_button_pin = right_button_pin
        self.__debounce_time = debounce_time

    def __debounce( self, button_pin: int ) -> bool:
        """Debounces the specified button pin.

        Args:
            button_pin (int): The GPIO pin of the button to debounce.

        Returns:
            bool: True if a falling edge was detected within the debounce time, False otherwise.
        """
        return self.__pi.wait_for_edge( button_pin, pigpio.FALLING_EDGE, wait_timeout = int( self.__debounce_time * 1000 ) )

    # TODO: Implement actual button logic here. For now, just print the button press event.
    def __left_button_callback( self ) -> bool:
        """Callback function for the left button press event.

        Returns:
            bool: True if the button was debounced, False otherwise.
        """
        if self.__debounce( self.__left_button_pin ):
            print( "Left button pressed" )
            return True
        return False

    # TODO: Implement actual button logic here. For now, just print the button press event.
    def __right_button_callback( self ) -> bool:
        """Callback function for the right button press event.

        Returns:
            bool: True if the button was debounced, False otherwise.
        """
        if self.__debounce( self.__right_button_pin ):
            print( "Right button pressed" )
            return True
        return False

    def start( self ):
        """Starts listening for button presses on the specified pins."""
        self.__pi.set_mode( self.__left_button_pin, pigpio.INPUT )
        self.__pi.set_mode( self.__right_button_pin, pigpio.INPUT )
        self.__pi.callback( self.__left_button_pin, pigpio.FALLING_EDGE, self.__left_button_callback )
        self.__pi.callback( self.__right_button_pin, pigpio.FALLING_EDGE, self.__right_button_callback )

    def stop( self ):
        """Stops listening for button presses and releases pigpio resources."""
        self.__pi.stop()
