import pigpio

from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput

from datetime import datetime
from typing import Tuple

#* NOTE: Change to use opencv once we have the converter assembled and verified
class CameraInterface:
    """Provides an interface to control the camera, capture images, and record video.

    This class handles camera configuration, image capture, and video recording using the Picamera2 library.
    It provides methods to start and stop recording, as well as capture still images.
    """

    def __init__( self, rtsp_stream_url: str, resolution: Tuple[ int, int ] = ( 640, 480 ), video_framerate: int = 30 ):
        """Initializes the CameraInterface with specified settings.

        Args:
            rtsp_stream_url (str): The URL for the RTSP stream. should be in the format 'rtsp://username:password@ip_address:port/path'.
            resolution (Tuple[int, int]): The desired video resolution (width, height). Defaults to (640, 480).
            video_framerate (int): The desired video framerate. Defaults to 30.
        """
        self.__camera: Picamera2 = Picamera2()
        self.__video_config = self.__camera.create_video_configuration( main={ "size": resolution, "format": "RGB888"}, controls={ 'FrameRate': video_framerate } )
        self.__output = FfmpegOutput( f'{ rtsp_stream_url }', audio=False )
        self.__video_encoder = H264Encoder( repeat=True, iperiod=video_framerate, framerate=video_framerate )
        self.__camera.configure( self.__video_config )

    def capture_image( self, image_path: str = f'./captured_images/{ datetime.now() }.jpg' ) -> str:
        """Captures an image from the camera and saves it to the specified path.

        Args:
            image_path (str): The path where the image should be saved. Defaults to './captured_images/{current timestamp}.jpg'.

        Returns:
            str: The path where the image was saved.
        """
        self.__camera.capture_file( image_path )
        print( f"Image saved as '{ image_path }'" )
        return image_path

    def start( self ) -> str:
        """Starts recording video to the specified RTSP stream.

        Returns:
            str: The filename of the output video file.
        """
        self.__camera.start_recording( encoder=self.__video_encoder, output=self.__output )
        return self.__output.output_filename

    def stop( self ):
        """Stops recording and releases camera resources."""
        self.__camera.close()

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
