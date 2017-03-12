import logging
import socket
from io import BytesIO
from typing import Dict, List

from .common import generate_pattern
from .vif_message import VIFMessage

from .vif_record import VIFRecord

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
        return self.send_message(message)

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
