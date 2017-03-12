from functools import wraps
import logging

from flask import Flask, abort, jsonify, make_response, request  # type: ignore
from six.moves import http_client
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
        'data': response.data()
    })


# @app.route('/api/handshake', methods=['GET'])
# @validate_gateway_parameters
# def handshake(venue_parameters):
#     gateway = VIFGateway(**venue_parameters)
#     message = VIFMessage.handshake()
#     data = gateway.send(message)
#     return jsonify({
#         'venue': venue_parameters,
#         'data': data
#     })


# @app.route('/api/init_transaction', methods=['POST'])
# @validate_gateway_parameters
# def init_transaction(venue_parameters):
#     gateway = VIFGateway(**venue_parameters)

#     workstation_id = request.json.get('workstation_id')
#     user_code = request.json.get('user_code', 'TKTBNTY')
#     session_no = request.json.get('session_no')
#     transaction_type = request.json.get('transaction_type', 1)
#     customer_reference = request.json.get('customer_reference')
#     tickets = request.json.get('tickets')
#     ticket_array = VIFTicketArray(record_code='q30')
#     if tickets:
#         for ticket in tickets:
#             ticket_array.add_ticket(**ticket)

#     message = VIFMessage.init_transaction(
#         workstation_id=workstation_id,
#         user_code=user_code,
#         session_no=session_no,
#         transaction_type=transaction_type,
#         customer_reference=customer_reference,
#         ticket_array=ticket_array
#     )
#     data = gateway.send(message)
#     return jsonify({
#         'venue': venue_parameters,
#         'data': data
#     })
