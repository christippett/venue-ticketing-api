from functools import wraps
import logging

from flask import Flask, abort, jsonify, make_response, request  # type: ignore
from werkzeug.exceptions import HTTPException  # type: ignore

from .vif_gateway import VIFGateway

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
        expected_params = ['site_name', 'auth_key', 'agent_no', 'host']

        venue_parameters = {
            'site_name': request.args.get('site_name'),
            'auth_key': request.args.get('auth_key'),
            'agent_no': request.args.get('agent_no'),
            'host': request.args.get('host')
        }

        return f(venue_parameters=venue_parameters, *args, **kwargs)
    return decorator


@app.errorhandler(Exception)
@app.errorhandler(400)
@app.errorhandler(404)
@app.errorhandler(500)
def error_view(error):
    code = 500 if not isinstance(error, HTTPException) else error.code
    return jsonify({
        'status_code': error.code,
        'response': str(error),
        'error': error.description
    }), code


@app.route('/api/get_data', methods=['GET'])
@validate_gateway_parameters
def get_tasks(venue_parameters):
    gateway = VIFGateway(**venue_parameters)
    data = gateway.get_data()
    return jsonify({
        'venue': venue_parameters,
        'data': data
    })


@app.route('/api/handshake', methods=['GET'])
@validate_gateway_parameters
def handshake(venue_parameters):
    gateway = VIFGateway(**venue_parameters)
    data = gateway.handshake()
    return jsonify({
        'venue': venue_parameters,
        'data': data
    })
