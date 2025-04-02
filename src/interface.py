import pigpio
import cv2

from pathlib import Path
from numpy import ndarray
from base64 import b64encode

from datetime import datetime
from typing import Tuple, Union, Optional

class CameraInterface:
    """Provides an interface to interact with a camera.

    This class handles camera initialization, image capturing, and frame retrieval.
    It uses OpenCV to interact with the camera hardware.
    """

    def __init__( self, resolution: Tuple[ int, int ] = ( 640, 480 ), video_framerate: int = 30, camera_device: Union[ str, int ] = 0, camera_manual_focus_value: int = -1 ) -> None:
        """Initializes the CameraInterface with the specified parameters.

        Args:
            resolution (Tuple[int, int]): The desired camera resolution. Defaults to (640, 480).
            video_framerate (int): The desired camera framerate. Defaults to 30.
            camera_device (Union[str, int]): The camera device identifier. Defaults to 0.
            camera_manual_focus_value (int): The manual focus value. Defaults to -1 (autofocus).
        """
        self.__camera_device = camera_device
        self.__resolution = resolution
        self.__video_framerate = video_framerate
        self.__camera_manual_focus_value = camera_manual_focus_value

        self.__camera = cv2.VideoCapture( self.__camera_device )
        if not self.__camera.isOpened():
            raise ValueError( f"Failed to open camera '{ self.__camera_device }'" )

        self.__camera.set( cv2.CAP_PROP_FRAME_WIDTH, self.__resolution[ 0 ] )
        self.__camera.set( cv2.CAP_PROP_FRAME_HEIGHT, self.__resolution[ 1 ] )
        self.__camera.set( cv2.CAP_PROP_FPS, self.__video_framerate )
        self.__camera.set( cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc( *'MJPG' ) )
        self.__camera.set( cv2.CAP_PROP_AUTOFOCUS, 1 if self.__camera_manual_focus_value == -1 else 0 )
        if self.__camera_manual_focus_value != -1:
            self.__camera.set( cv2.CAP_PROP_FOCUS, camera_manual_focus_value )
        self.__camera.set( cv2.CAP_PROP_AUTO_EXPOSURE, 0.25 )

        self.streaming = False

    def capture_image( self, image_path: str = f'./captured_images/{ datetime.now().ctime() }.jpg' ) -> Tuple[ Optional[ str ], Optional[ str ] ]:
        """Captures an image from the camera and saves it to the specified path.

        Args:
            image_path (str): The path to save the captured image. Defaults to './captured_images/{current_time}.jpg'.

        Returns:
            Optional[str]: The path to the saved image if successful, None otherwise.
        """
        frame = self.get_last_frame()
        if frame is None:
            print( 'Please start camera first' )
            return None

        Path( image_path ).parent.mkdir( parents=True, exist_ok=True )
        valid = cv2.imwrite( image_path, frame )
        if not valid:
            print( f"Failed to save image at '{ image_path }'" )
            return None, None

        return image_path, frame

    def get_last_frame( self ) -> Optional[ ndarray ]:
        """Retrieves the last frame captured by the camera.

        Returns:
            Optional[ndarray]: The last captured frame as a NumPy array if successful, None otherwise.
        """
        valid, frame = self.__camera.read()
        if not valid:
            print( 'Failed to capture image' )
            return None
        return frame

    def as_b64_str( self, img: ndarray ) -> str:
        """Encodes the given image as a base64 string.

        Args:
            img (ndarray): The image to encode.

        Returns:
            str: The base64 encoded image string.
        """
        return f'data:image/jepg;base64,{ b64encode( cv2.imencode( '.jpg', img )[1] ).decode( 'utf-8' ) }'
    def start( self ) -> str:
        """Starts the camera stream.

        Returns:
            str: An empty string.
        """
        if not self.__camera.isOpened():
            self.__init__( camera_device=self.__camera_device, resolution=self.__resolution, video_framerate=self.__video_framerate, camera_manual_focus_value=self.__camera_manual_focus_value )
        self.streaming = True

    def stop( self ):
        """Stops the camera stream and releases camera resources."""
        self.__camera.release()
        # if self.__stream_thread.is_alive():
        #     self.__stream_thread.join( timeout=self.__stream_thread_timeout )

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
        self.in_use = False

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
        self.in_use = True

    def stop( self ):
        """Stops listening for button presses and releases pigpio resources."""
        self.__pi.stop()
        self.in_use = False
