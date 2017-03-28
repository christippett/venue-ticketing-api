from functools import wraps
import logging
import base64
import json
import os

from flask import Flask, abort, jsonify, make_response, request  # type: ignore
from flask_cors import cross_origin  # type: ignore
from werkzeug.exceptions import HTTPException  # type: ignore


from .vif_gateway import VIFGateway
from .vif_message import VIFMessage
from .vif_detail_array import VIFTicketArray

PROJECT_ID = 'ticket-bounty'
APP_ENV = os.environ.get('APP_ENV', 'dev')


app = Flask(__name__)


def validate_gateway_parameters(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        venue_parameters = {
            'site_name': request.headers.get('X-VIF-SITENAME'),
            'auth_info': request.headers.get('X-VIF-AUTHINFO'),
            'host': request.headers.get('X-VIF-HOST')
        }
        return f(venue_parameters=venue_parameters, *args, **kwargs)
    return decorator


@app.errorhandler(500)
def unexpected_error(e):
    """Handle exceptions by returning swagger-compliant json."""
    logging.exception('An error occured while processing the request.')
    response = jsonify({
        'code': 500,
        'message': 'Exception: {}'.format(e)})
    response.status_code = 500
    return response


@app.route('/', methods=['GET'])
def index():
    return '', 200


@app.route('/_ah/health', methods=['GET'])
def gae_health_check():
    return 'Healthy!'


@app.route('/api/get_data', methods=['GET'])
@validate_gateway_parameters
def get_tasks(venue_parameters):
    gateway = VIFGateway(**venue_parameters)
    response = gateway.get_data()  # type: VIFMessage
    return jsonify({
        'data': response.friendly_data()
    })


@app.route('/api/handshake', methods=['GET'])
@validate_gateway_parameters
def handshake(venue_parameters):
    gateway = VIFGateway(**venue_parameters)
    response = gateway.handshake()  # type: VIFMessage
    return jsonify({
        'data': response.friendly_data()
    })


@app.route('/api/verify_booking', methods=['GET'])
@validate_gateway_parameters
def verify_booking(venue_parameters):
    gateway = VIFGateway(**venue_parameters)

    # GET parameters
    alternate_booking_key = request.args.get('alternate_booking_key')

    response = gateway.verify_booking(alternate_booking_key)  # type: VIFMessage
    return jsonify({
        'data': response.friendly_data()
    })


@app.route('/api/get_session_seats', methods=['GET'])
@validate_gateway_parameters
def get_session_seats(venue_parameters):
    gateway = VIFGateway(**venue_parameters)

    # GET parameters
    session_number = request.args.get('session_number')
    availability = request.args.get('availability', 0)

    response = gateway.get_session_seats(session_number, availability)  # type: VIFMessage
    return jsonify({
        'data': response.data()
    })


@app.route('/api/init_transaction', methods=['POST'])
@validate_gateway_parameters
def init_transaction(venue_parameters):
    gateway = VIFGateway(**venue_parameters)

    # POST parameters
    data = request.json.get('data')

    response = gateway.init_transaction(data=data)  # type: VIFMessage
    return jsonify({
        'data': response.friendly_data()
    })


@app.route('/api/free_seats', methods=['POST'])
@validate_gateway_parameters
def free_seats(venue_parameters):
    gateway = VIFGateway(**venue_parameters)

    # POST parameters
    data = request.json.get('data')

    response = gateway.free_seats(data=data)  # type: VIFMessage
    return jsonify({
        'data': response.friendly_data()
    })


@app.route('/api/commit_transaction', methods=['POST'])
@validate_gateway_parameters
def commit_transaction(venue_parameters):
    gateway = VIFGateway(**venue_parameters)

    # POST parameters
    data = request.json.get('data')

    response = gateway.commit_transaction(data=data)  # type: VIFMessage
    return jsonify({
        'data': response.friendly_data()
    })


# GOOGLE CLOUD ENDPOINTS AUTHENTICATION INFORMATION
def _base64_decode(encoded_str):
    # Add paddings manually if necessary.
    num_missed_paddings = 4 - len(encoded_str) % 4
    if num_missed_paddings != 4:
        encoded_str += b'=' * num_missed_paddings
    return base64.b64decode(encoded_str).decode('utf-8')


def auth_info():
    """Retrieves the authenication information from Google Cloud Endpoints."""
    encoded_info = request.headers.get('X-Endpoint-API-UserInfo', None)

    if encoded_info:
        info_json = _base64_decode(encoded_info)
        user_info = json.loads(info_json)
    else:
        user_info = {'id': 'anonymous'}

    return jsonify(user_info)


@app.route('/auth/info/googlejwt', methods=['GET'])
def auth_info_google_jwt():
    """Auth info with Google signed JWT."""
    return auth_info()


@app.route('/auth/info/googleidtoken', methods=['GET'])
def auth_info_google_id_token():
    """Auth info with Google ID token."""
    return auth_info()


@app.route('/auth/info/firebase', methods=['GET'])
@cross_origin(send_wildcard=True)
def auth_info_firebase():
    """Auth info with Firebase auth."""
    return auth_info()
