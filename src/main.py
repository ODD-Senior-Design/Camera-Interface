from flask import Flask, Response, request, jsonify, abort
from flask_cors import CORS
from flask_socketio import SocketIO

import asyncio
import contextlib
import websockets as ws

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
camera_device: int = int( getenv( 'CAMERA_DEVICE', 0 ) )
video_resolution: Tuple[ int, int ] = tuple( map( int, getenv( 'VIDEO_RESOLUTION', '640x480' ).split( 'x' ) ) )
video_framerate: int = int( getenv( 'VIDEO_FRAMERATE', 30 ) )
focus: int = int( getenv( "CAMERA_FOCUS_AMOUNT", -1 ) )

left_button_pin = int( getenv( 'LEFT_BUTTON_PIN', 18 ) )
right_button_pin = int( getenv( 'RIGHT_BUTTON_PIN', 23 ) )
debounce_time = float( getenv( 'DEBOUNCE_TIME', 0.2 ) )

webhook: Flask = Flask( getenv( 'WEBHOOK_NAME', 'Interface Webhook' ) )
CORS( webhook, origins='*' )
bind_address: str = getenv( 'BIND_ADDRESS', '0.0.0.0' )
bind_port: int = int( getenv( 'BIND_PORT', 3000 ) )

stream_ws: SocketIO = SocketIO( webhook, cors_allowed_origins='*' )
websocket_port: int = int( getenv( 'WEBSOCKET_PORT', '3333' ) )

camera = CameraInterface( video_resolution, video_framerate, camera_device )
button = ButtonInterface( left_button_pin, right_button_pin, debounce_time )

@stream_ws.on( 'connect', namespace='/stream' )
def on_connect() -> None:
    print( 'Websocket client connected' )
    stream_ws.start_background_task( send_frames )
    
def send_frames() -> None:
    camera.start()
    last_frame = camera.get_last_frame()
    while last_frame is not None:
        frame_payload = camera.as_b64_str( last_frame )
        stream_ws.sleep(0)
        stream_ws.emit( 'message', { "frame" : frame_payload }, namespace='/stream' )
        last_frame = camera.get_last_frame()
        current_frame_time = datetime.now()
        if debug: int( f'Frame timing: { current_frame_time - last_frame_time }' )
        last_frame_time = current_frame_time

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

    if not camera.streaming:
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
    if camera.streaming:
        camera.stop()
    if button.in_use:
        button.stop()

def main() -> None:
    load_dotenv()
    exit_handler( on_exit )
    print( f"Using camera: '{ camera_device }' " )
    if path.exists( '/sys/firmware/devicetree/base/model' ):
        button.start()
    stream_ws.run( app=webhook, host=bind_address, port=bind_port, debug=debug )
    #webhook.run( host=bind_address, port=bind_port, debug=debug )

if __name__ == '__main__':
    main()
