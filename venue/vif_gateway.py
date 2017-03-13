import logging
import socket
from io import BytesIO
from typing import Dict, List

from .common import generate_pattern
from .vif_message import VIFMessage

from .vif_record import VIFRecord
from .vif_detail_array import VIFTicketArray

logger = logging.getLogger(__name__)


class VIFGatewayError(Exception):
    pass


class VIFGateway(object):
    DEFAULT_PORT = 4016
    VIFGatewayError = VIFGatewayError

    def __init__(self, host: str=None, auth_info: str=None, site_name: str=None,
                 comment: str=None, gateway_type: int=0):
        self.host = host
        self.auth_info = auth_info
        self.site_name = site_name
        self.gateway_type = gateway_type
        self.comment = comment or 'Ticket Bounty VIF Gateway'

    def header_data(self) -> Dict:
        return {
            'site_name': self.site_name,
            'packet_id': generate_pattern(4),
            'comment': self.comment,
            'auth_info': self.auth_info,
            'gateway_type': self.gateway_type  # 0=Ticketing, 1=Concessions, 2=Voucher
        }

    def _get_sock_response(self, sock, size=8192) -> BytesIO:
        # Write response to stream
        resp = BytesIO()
        while True:
            r = sock.recv(size)
            resp.write(r)
            # Response is terminated by an ETX (ascii 3)
            if chr(3) in r.decode():
                break
        resp.seek(0)
        return resp

    def send_message(self, message: VIFMessage) -> VIFMessage:
        message_content = message.content()
        logger.debug("REQUEST: %s", message_content)
        # Request must be sent as bytes and terminated by an ETX (ascii 3)
        encoded_message_content = (message_content + chr(3)).encode()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(15)
        sock.connect((self.host, self.DEFAULT_PORT))
        sock.sendall(encoded_message_content)
        response_stream = self._get_sock_response(sock, size=64)
        sock.close()
        response_text = response_stream.getvalue().decode()
        logger.debug("RESPONSE: %s", response_text)
        return VIFMessage(content=response_text)

    def handshake(self) -> VIFMessage:
        message = VIFMessage()
        message.set_request_header(request_code=1, **self.header_data())
        response = self.send_message(message)
        if len(response.body) == 1:
            response.body[0].record_code = 'p01'
        return response

    def get_data(self, detail_required: int=2) -> VIFMessage:
        """
        Record code: 2
        Description: This request will receive VIF records from the host
            ticketing system. The specific records required are not specified
            by the request, but rather all records and fields.
        Comments: If a detail of "2" is supplied, the VIF records returned
            contains a subset of the available VIF data, which is sufficient to
            provide web based information services and a booking facility.
            Other detail values are reserved for other applications such as
            export of statistical information, etc.
        """
        message = VIFMessage()
        message.set_request_header(request_code=2, **self.header_data())
        body_data = {'detail_required': detail_required}
        body_record = VIFRecord(record_code='q02', data=body_data)
        message.add_body_record(body_record)
        return self.send_message(message)

    def verify_booking(self, alternate_booking_key: str) -> VIFMessage:
        """
        Record code: 42
        Description: Returns key information about a booking if the booking is
            still current, otherwise an error is returned.
        """
        message = VIFMessage()
        message.set_request_header(request_code=42, **self.header_data())
        body_data = {'alternate_booking_key': alternate_booking_key}
        body_record = VIFRecord(record_code='q42', data=body_data)
        message.add_body_record(body_record)
        response = self.send_message(message)
        if len(response.body) == 1:
            response.body[0].record_code = 'p42'
        return response

    def get_session_seats(self, session_number: int, availability: int=0) -> VIFMessage:
        """
        Record code: 20
        Description: Can be used to retrieve a snapshot of the current seating
            status for the specified session.
        Availability:
            0=Get All Seats
            1=Available
            2=Unavailable
        Body: q20 record
        Response: pl4 record

        """
        message = VIFMessage()
        message.set_request_header(request_code=20, **self.header_data())
        body_data = {
            'session_number': session_number,
            'availability': availability
        }
        body_record = VIFRecord(record_code='q20', data=body_data)
        message.add_body_record(body_record)
        return self.send_message(message)

    def init_transaction(self, data: Dict) -> VIFMessage:
        """
        Record code: 30
        Description: This request will cause an “init” internet booking to be
            recorded. That is, it will commence a booking transaction and
            tickets will be reserved. The transaction will remain incomplete
            until the client application performs a “Commit Internet Booking”.
        Body: q30 record
        Response: p30 record
        """
        message = VIFMessage()
        message.set_request_header(request_code=30, **self.header_data())
        body_record = VIFRecord(record_code='q30', data=data)
        message.add_body_record(body_record)
        return self.send_message(message)

    def free_seats(self, data: Dict) -> VIFMessage:
        """
        Record code: 30
        Description: This request will cause an “init” internet booking to be
            recorded. That is, it will commence a booking transaction and
            tickets will be reserved. The transaction will remain incomplete
            until the client application performs a “Commit Internet Booking”.
        Body: q30 record
        Response: p30 record
        """
        message = VIFMessage()
        message.set_request_header(request_code=17, **self.header_data())
        body_record = VIFRecord(record_code='q17', data=data)
        message.add_body_record(body_record)
        return self.send_message(message)

    def commit_transaction(self, data: Dict) -> VIFMessage:
        """
        Record code: 31
        Description: This request will cause a “commit” internet booking
            transaction to be recorded. That is, it will be commit an online
            payment transaction and mark it as having successfully transferred
            online funds. A transaction must have previously been commenced by
            “Init Internet Booking”.
        Body: q31 record
        Response: p31 record
        """
        message = VIFMessage()
        message.set_request_header(request_code=31, **self.header_data())
        body_record = VIFRecord(record_code='q31', data=data)
        message.add_body_record(body_record)
        return self.send_message(message)
