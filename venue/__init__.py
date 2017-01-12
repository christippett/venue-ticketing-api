from functools import wraps
import logging

from flask import Flask, abort, jsonify, make_response, request  # type: ignore
from werkzeug.exceptions import HTTPException  # type: ignore

from .vif_gateway import VIFGateway
from .vif_message import VIFMessage
from .vif_ticket_array import VIFTicketArray

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
            'auth_key': request.headers.get('VIF_AUTH_KEY'),
            'agent_no': request.headers.get('VIF_AGENT_NO'),
            'host': request.headers.get('VIF_HOST')
        }
        # TODO: Perform a handshake to validate credentials

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
    message = VIFMessage.get_data()
    data = gateway.send(message)
    return jsonify({
        'venue': venue_parameters,
        'data': data
    })


@app.route('/api/handshake', methods=['GET'])
@validate_gateway_parameters
def handshake(venue_parameters):
    gateway = VIFGateway(**venue_parameters)
    message = VIFMessage.handshake()
    data = gateway.send(message)
    return jsonify({
        'venue': venue_parameters,
        'data': data
    })


@app.route('/api/init_transaction', methods=['POST'])
@validate_gateway_parameters
def init_transaction(venue_parameters):
    gateway = VIFGateway(**venue_parameters)

    workstation_id = request.json.get('workstation_id')
    user_code = request.json.get('user_code', 'TKTBNTY')
    session_no = request.json.get('session_no')
    transaction_type = request.json.get('transaction_type', 1)
    customer_reference = request.json.get('customer_reference')
    tickets = request.json.get('tickets')
    ticket_array = VIFTicketArray()
    if tickets:
        for ticket in tickets:
            ticket_array.add_ticket(**ticket)

    message = VIFMessage.init_transaction(
        workstation_id=workstation_id,
        user_code=user_code,
        session_no=session_no,
        transaction_type=transaction_type,
        customer_reference=customer_reference,
        ticket_array=ticket_array
    )
    data = gateway.send(message)
    return jsonify({
        'venue': venue_parameters,
        'data': data
    })
