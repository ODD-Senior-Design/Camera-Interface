from flask import Flask, Response, request, jsonify, abort
from flask_socketio import SocketIO

from os import getenv, path
from atexit import register as exit_handler
from datetime import datetime
from typing import Tuple, Dict, Union

from interface import CameraInterface, ButtonInterface

api_url = getenv( 'API_URL', 'http://localhost:5000' )
datetime_format = getenv( 'DATETIME_FORMAT', '%Y-%m-%dT%H:%M:%S' )

images_save_dir: str = getenv( 'IMAGES_SAVE_DIRECTORY', './captured_images' )
camera_device: Union[ int, str ] = getenv( 'CAMERA_DEVICE', '0' )
video_resolution: Tuple[ int, int ] = map( int, getenv( 'VIDEO_RESOLUTION', '640x480' ).split( 'x' ) )
video_framerate: int = int( getenv( 'VIDEO_FRAMERATE', '30' ) )

left_button_pin = int( getenv( 'LEFT_BUTTON_PIN', '18' ) )
right_button_pin = int( getenv( 'RIGHT_BUTTON_PIN', '23' ) )
debounce_time = float( getenv( 'DEBOUNCE_TIME', '0.2' ) )

webhook: Flask = Flask( getenv( 'WEBHOOK_NAME', 'Interface API' ) )
stream_ws: SocketIO = SocketIO( webhook )
bind_address: str = getenv( 'BIND_ADDRESS', '0.0.0.0' )
bind_port: int = int( getenv( 'BIND_PORT', '3000' ) )

camera = CameraInterface( video_resolution, video_framerate, camera_device )
button = ButtonInterface( left_button_pin, right_button_pin, debounce_time )

@stream_ws.on( 'connect', namespace='/stream' )
def start_stream() -> Response:
    camera.start()

    while last_frame := camera.get_last_frame():
        frame_payload = camera.as_jpg_bytes( last_frame )
        stream_ws.emit( 'stream', { 'frame_bytes': frame_payload } )

@stream_ws.on( 'disconnect', namespace='/stream' )
def close_stream() -> None:
    camera.stop()

@webhook.route( '/capture', methods=[ 'POST' ] )
def capture() -> Response:
    """Captures an image from the camera and returns the image path and timestamp.

    Expects a JSON payload with a dictionary of IDs. These IDs are used to construct the image filename.
    Returns a JSON response containing the URI of the captured image and the timestamp.
    """
    ids: Dict[ str, str ] = request.get_json()
    captured_time = datetime.now().strftime( datetime_format )
    joined_ids = '_'.join( ids.values() )
    image_path = f"{ images_save_dir }/{ joined_ids }{ '_' if joined_ids != '' else '' }{ captured_time }.jpg"

    if not camera.in_use:
        abort( 500, 'Camera is not available. Please check physical connection and if stream is running.' )

    image_path = camera.capture_image( image_path )
    if not image_path:
        abort( 500, 'Failed to capture and save image.' )

    absolute_image_path = path.abspath( image_path )

    return jsonify( { "uri": f'file://{ absolute_image_path }', "image_timestamp": captured_time } )

def on_exit() -> None:
    """Cleanup function to be executed on exit.

    Stops the camera and button interfaces.
    """
    print( 'Closing camera and button interface if in use...' )
    if camera.in_use:
        camera.stop()
    if button.in_use:
        button.stop()

def main() -> None:
    """Main function to start the application.

    Registers an exit handler, starts the Flask webhook, and initializes the camera and button interfaces.
    """
    exit_handler( on_exit )
    webhook.run( host=bind_address, port=bind_port )
    button.start()

if __name__ == '__main__':
    main()
