# Imports
from flask import Flask, Response, request, jsonify

from os import getenv, path
from datetime import datetime
from typing import Tuple, Dict

from interface import CameraInterface, ButtonInterface

api_url = getenv( 'API_URL', 'http://localhost:5000' )
datetime_format = getenv( 'DATETIME_FORMAT', '%Y-%m-%dT%H:%M:%S' )

images_save_dir: str = getenv( 'IMAGES_SAVE_DIRECTORY', './captured_images' )
video_stream_url: str = getenv( 'VIDEO_STREAM_URL', 'rtsp://odd:oddinterface@localhost:3333' )
video_resolution: Tuple[ int, int ] = map( int, getenv( 'VIDEO_RESOLUTION', '640x480' ).split( 'x' ) )
video_framerate: int = int( getenv( 'VIDEO_FRAMERATE', '30' ) )

left_button_pin = int( getenv( 'LEFT_BUTTON_PIN', '18' ) )
right_button_pin = int( getenv( 'RIGHT_BUTTON_PIN', '23' ) )
debounce_time = int( getenv( 'DEBOUNCE_TIME', '0.2' ) )

webhook: Flask = Flask( getenv( 'WEBHOOK_NAME', 'Interface API' ) )
bind_address: str = getenv( 'BIND_ADDRESS', '0.0.0.0' )
bind_port: int = int( getenv( 'BIND_PORT', '3000' ) )

camera = CameraInterface( f'rtsp://{ api_url }/stream', video_resolution, video_framerate )
button = ButtonInterface( left_button_pin, right_button_pin, debounce_time )

@webhook.route( '/capture', methods=[ 'POST' ] )
def capture() -> Response:
    ids: Dict[ str, str ] = request.get_json()
    captured_time = datetime.now().strftime( datetime_format )
    joined_ids = '_'.join( ids.values() )
    image_path = f"{ images_save_dir }/{ joined_ids }{ '_' if joined_ids != '' else '' }{ captured_time }.jpg"

    image_path = camera.capture_image( image_path )

    absolute_image_path = path.abspath( image_path )

    return jsonify( { "uri": f'file://{ absolute_image_path }', "image_timestamp": captured_time } )

def main() -> None:
    webhook.run( host=video_resolution, port=video_framerate )
    camera.start()

    button.start()

if __name__ == '__main__':
    main()