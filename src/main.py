from flask import Flask, Response, request, jsonify, abort
from flask_cors import CORS
from flask_socketio import SocketIO
from threading import Event

from dotenv import load_dotenv
from os import getenv, path
from atexit import register as exit_handler
from datetime import datetime
from typing import Tuple, Dict

from interface import CameraInterface, ButtonInterface

debug = getenv( 'DEBUG', '0' ) == '1'

api_url = getenv( 'API_URL', 'http://localhost:5000' )
datetime_format = getenv( 'DATETIME_FORMAT', '%Y-%m-%dT%H:%M:%S' )

images_save_dir: str = getenv( 'IMAGES_SAVE_DIRECTORY', './captured_images' )
camera_device: int = int( getenv( 'CAMERA_DEVICE', '0' ) )
video_resolution: Tuple[ int, int ] = tuple( map( int, getenv( 'VIDEO_RESOLUTION', '640x480' ).split( 'x' ) ) )
video_framerate: int = int( getenv( 'VIDEO_FRAMERATE', '30' ) )
focus: int = int( getenv( "CAMERA_FOCUS_AMOUNT", '-1' ) )

left_button_pin = int( getenv( 'LEFT_BUTTON_PIN', '18' ) )
right_button_pin = int( getenv( 'RIGHT_BUTTON_PIN', '23' ) )
debounce_time = float( getenv( 'DEBOUNCE_TIME', '0.2' ) )

webhook: Flask = Flask( getenv( 'WEBHOOK_NAME', 'Interface Webhook' ) )
CORS( webhook, origins='*' )
bind_address: str = getenv( 'BIND_ADDRESS', '0.0.0.0' )
bind_port: int = int( getenv( 'BIND_PORT', '3000' ) )

stream_ws: SocketIO = SocketIO( webhook, cors_allowed_origins='*' )
camera_live = Event()

camera = CameraInterface( video_resolution, video_framerate, camera_device )
button = ButtonInterface( left_button_pin, right_button_pin, debounce_time )


def send_frames( live ) -> None:
    """Sends frames from the camera over the websocket.

    Continuously retrieves the last frame from the camera and emits it over the '/stream' namespace.
    Prints frame timing information if debug mode is enabled.
    """
    last_frame = camera.get_last_frame()
    last_frame_time = datetime.now()
    while live.is_set():
        if last_frame is None:
            last_frame = camera.get_last_frame()
        frame_payload = camera.as_b64_str( last_frame )
        stream_ws.sleep(0)
        stream_ws.emit( 'message', { "frame" : frame_payload }, namespace='/stream' )
        last_frame = camera.get_last_frame()
        current_frame_time = datetime.now()
        if debug: print( f'Frame timing: { current_frame_time - last_frame_time }' )
        last_frame_time = current_frame_time

@stream_ws.on( 'connect', namespace='/stream' )
def on_connect() -> None:
    """Handles the connection of a websocket client.

    Prints a message to the console indicating the connection. Starts the camera and begins sending frames.
    """
    print( 'Websocket client connected' )
    camera.start()
    camera_live.set()
    stream_ws.start_background_task( send_frames, camera_live )

@stream_ws.on( 'disconnect', namespace='/stream' )
def on_disconnect() -> None:
    """Handles the disconnection of a websocket client.

    Prints a message to the console indicating the disconnection. Stops the camera.
    """
    print( 'Websocket client disconnected' )
    camera_live.clear()
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
    image_path = f"{ images_save_dir }/{ joined_ids }.jpg"

    if not camera.streaming:
        abort( 500, 'Camera is not available. Please check physical connection and if stream is running.' )

    image_path, last_frame = camera.capture_image( image_path )
    if not image_path:
        abort( 500, 'Failed to capture and save image.' )

    absolute_image_path = path.abspath( image_path )

    return jsonify( { "uri": f'file://{ absolute_image_path }',"image_b64": camera.as_b64_str( last_frame ), "image_timestamp": captured_time } )

def on_exit() -> None:
    """Cleanup function to be executed on exit.

    Stops the camera and button interfaces.
    """
    print( 'Closing camera and button interface if in use...' )
    if camera.streaming:
        camera_live.clear()
        camera.stop()
    if button.in_use:
        button.stop()

def main() -> Flask:
    """Main function to initialize and run the application.

    Loads environment variables, registers the exit handler, starts the button interface if available,
    and runs the Flask webhook and websocket.
    """
    load_dotenv( './.env' )
    exit_handler( on_exit )
    if path.exists( '/sys/firmware/devicetree/base/model' ):
        print( 'Starting button interface...')
        button.start()
    print( f'Using camera: { camera_device }' )
    print( 'Starting webhook and websocket connection...')
    if not debug:
        return webhook
    stream_ws.run( app=webhook, host=bind_address, port=bind_port, debug=debug )

if __name__ == '__main__':
    print( 'Running python file, debug flag is automatically set...' )
    debug=True
    main()
