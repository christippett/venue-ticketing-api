from functools import wraps
import logging

from flask import Flask, abort, jsonify, make_response, request  # type: ignore
from six.moves import http_client
from werkzeug.exceptions import HTTPException  # type: ignore

from .vif_gateway import VIFGateway
from .vif_message import VIFMessage
from .vif_detail_array import VIFTicketArray

app = Flask(__name__)

# Configure logging
handler = logging.StreamHandler()
handler.setLevel(logging.NOTSET)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)
app.logger.setLevel(logging.DEBUG)


def validate_gateway_parameters(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        venue_parameters = {
            'site_name': request.headers.get('VIF_SITE_NAME'),
            'auth_info': request.headers.get('VIF_AUTH_INFO'),
            'host': request.headers.get('VIF_HOST')
        }
        # TODO: Perform a handshake to validate credentials

        return f(venue_parameters=venue_parameters, *args, **kwargs)
    return decorator


@app.errorhandler(http_client.INTERNAL_SERVER_ERROR)
def unexpected_error(e):
    """Handle exceptions by returning swagger-compliant json."""
    logging.exception('An error occured while processing the request.')
    response = jsonify({
        'code': http_client.INTERNAL_SERVER_ERROR,
        'message': 'Exception: {}'.format(e)})
    response.status_code = http_client.INTERNAL_SERVER_ERROR
    return response


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
