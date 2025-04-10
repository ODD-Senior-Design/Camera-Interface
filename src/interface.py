import pigpio
import cv2

from pathlib import Path
from numpy import ndarray
from base64 import b64encode

from datetime import datetime
from typing import Tuple, Union, Optional

class CameraInterface:
    """Interfaces with a camera for capturing images and video.

    Initializes a camera instance, configures settings like resolution and framerate,
    and provides methods for capturing images, retrieving frames, and encoding images.
    """

    def __init__( self, resolution: Tuple[int, int] = (640, 480), video_framerate: int = 30, camera_device: Union[str, int] = 0, camera_manual_focus_value: int = -1 ) -> None:
        """Initializes the camera interface with given parameters.

        Args:
            resolution: The desired camera resolution (width, height). Defaults to (640, 480).
            video_framerate: The desired camera framerate. Defaults to 30.
            camera_device: The camera device identifier (e.g., 0 for the default camera). Defaults to 0.
            camera_manual_focus_value: The manual focus value. Defaults to -1 (autofocus).
        """
        self.__camera_device = camera_device
        self.__resolution = resolution
        self.__video_framerate = video_framerate
        self.__camera_manual_focus_value = camera_manual_focus_value

        self.__camera = cv2.VideoCapture( self.__camera_device )
        if not self.__camera.isOpened():
            raise ValueError( f"Failed to open camera '{ self.__camera_device }'" )

        self.__camera.set( cv2.CAP_PROP_FRAME_WIDTH, float( self.__resolution[ 0 ] ) )
        self.__camera.set( cv2.CAP_PROP_FRAME_HEIGHT, float( self.__resolution[ 1 ] ) )
        self.__camera.set( cv2.CAP_PROP_FPS, self.__video_framerate )
        self.__camera.set( cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc( *'MJPG' ) )
        self.__camera.set( cv2.CAP_PROP_AUTOFOCUS, 1 if self.__camera_manual_focus_value == -1 else 0 )
        if self.__camera_manual_focus_value != -1:
            self.__camera.set( cv2.CAP_PROP_FOCUS, camera_manual_focus_value )
        self.__camera.set( cv2.CAP_PROP_AUTO_EXPOSURE, 0.25 )

        self.streaming = False

    def capture_image(self, image_path: str = f'./captured_images/{datetime.now().ctime()}.jpg') -> Tuple[Optional[str], Optional[ndarray]]:
        """Captures an image and saves it to the specified path.

        Retrieves the last frame from the camera, creates the necessary directories,
        and saves the image to the given path.

        Args:
            image_path: The path where the image will be saved. Defaults to './captured_images/{current_time}.jpg'.

        Returns:
            A tuple containing the image path and the captured frame if successful, or (None, None) otherwise.
        """
        frame = self.get_last_frame()
        if frame is None:
            print( 'Please start camera first' )
            return None, None

        Path( image_path ).parent.mkdir( parents=True, exist_ok=True )
        valid = cv2.imwrite( image_path, frame )
        if not valid:
            print( f"Failed to save image at '{ image_path }'" )
            return None, None

        return image_path, frame

    def get_last_frame(self) -> Optional[ndarray]:
        """Retrieves the last frame captured by the camera.

        Reads a frame from the camera and returns it as a NumPy array.

        Returns:
            The last captured frame as a NumPy array, or None if capturing failed.
        """
        valid, frame = self.__camera.read()
        if not valid:
            print( 'Failed to capture image' )
            return None
        return frame

    def as_b64_str(self, img: ndarray) -> str:
        """Encodes an image as a base64 string.

        Converts the given image to a JPEG format, encodes it in base64,
        and returns the result as a string.

        Args:
            img: The image to encode (NumPy array).

        Returns:
            The base64 encoded image string.
        """

        return f'data:image/jpeg;base64,{ b64encode( cv2.imencode( ".jpg", img )[1] ).decode( "utf-8" ) }'

    def start(self):
        """Starts the camera stream.

        Re-initializes the camera if it's not already opened and sets the streaming flag to True.
        """
        if not self.__camera.isOpened():
            self.__init__( camera_device=self.__camera_device, resolution=self.__resolution, video_framerate=self.__video_framerate, camera_manual_focus_value=self.__camera_manual_focus_value )
        self.streaming = True

    def stop(self):
        """Stops the camera stream and releases resources.

        Releases the camera object to free up resources.
        """
        self.__camera.release()

class ButtonInterface:
    """Interfaces with physical buttons for input events.

    Handles button press detection and debouncing using the pigpio library.
    Provides methods to start and stop listening for button presses on specified pins.
    """
    def __init__(self, left_button_pin, right_button_pin, debounce_time=0.2):
        """Initializes the button interface with specified pins and debounce time.

        Args:
            left_button_pin: The GPIO pin for the left button.
            right_button_pin: The GPIO pin for the right button.
            debounce_time: The debounce time in seconds. Defaults to 0.2.
        """
        self.__pi = pigpio.pi()
        self.__left_button_pin = left_button_pin
        self.__right_button_pin = right_button_pin
        self.__debounce_time = debounce_time
        self.in_use = False

    def __debounce(self, button_pin: int) -> bool:
        """Debounces a button pin to prevent spurious readings.

        Waits for a falling edge on the specified pin within the debounce time.

        Args:
            button_pin: The GPIO pin of the button.

        Returns:
            True if a falling edge was detected within the debounce time, False otherwise.
        """
        return self.__pi.wait_for_edge( button_pin, pigpio.FALLING_EDGE, wait_timeout = int( self.__debounce_time * 1000 ) )

    # TODO: Implement actual button logic here. For now, just print the button press event.
    def __left_button_callback(self) -> bool:
        """Handles the left button press event.

        Debounces the left button pin and prints a message if a valid press is detected.

        Returns:
            True if the button press was debounced, False otherwise.
        """
        if self.__debounce( self.__left_button_pin ):
            print( "Left button pressed" )
            return True
        return False

    # TODO: Implement actual button logic here. For now, just print the button press event.
    def __right_button_callback(self) -> bool:
        """Handles the right button press event.

        Debounces the right button pin and prints a message if a valid press is detected.

        Returns:
            True if the button press was debounced, False otherwise.
        """
        if self.__debounce( self.__right_button_pin ):
            print( "Right button pressed" )
            return True
        return False

    def start(self):
        """Starts listening for button presses.

        Sets up the GPIO pins for input and attaches callbacks for button press events.
        """
        self.__pi.set_mode( self.__left_button_pin, pigpio.INPUT )
        self.__pi.set_mode( self.__right_button_pin, pigpio.INPUT )
        self.__pi.callback( self.__left_button_pin, pigpio.FALLING_EDGE, self.__left_button_callback )
        self.__pi.callback( self.__right_button_pin, pigpio.FALLING_EDGE, self.__right_button_callback )
        self.in_use = True

    def stop(self):
        """Stops listening for button presses and releases resources.

        Stops the pigpio interface and releases associated resources.
        """
        self.__pi.stop()
        self.in_use = False
