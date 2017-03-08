import logging
import socket
import uuid
from collections import defaultdict
from io import BytesIO
from typing import Dict

from .vif_message import VIFMessage

logger = logging.getLogger(__name__)


class VIFGatewayError(Exception):
    pass


class VIFGateway(object):
    DEFAULT_PORT = 4016
    VIFGatewayError = VIFGatewayError

    def __init__(self, host=None, auth_key=None, agent_no=None,
                 site_name=None):
        self.host = host
        self.auth_key = auth_key
        self.agent_no = agent_no
        self.site_name = site_name

    @property
    def gateway_headers(self) -> Dict:
        return {
            'site_name': self.site_name,
            'packet_id': self.random_pattern(8),
            'comment': 'Ticket Bounty VIF Gateway v0.1',
            'auth_info': "%s%s" % (self.auth_key, self.agent_no),
            'gateway_type': 0
        }

    def random_pattern(self, length: int) -> str:
        return str(uuid.uuid4()).upper()[:length]

    def parse_sock(self, sock, size=8192) -> BytesIO:
        # Write response to stream
        resp = BytesIO()
        while True:
            r = sock.recv(size)
            resp.write(r)
            if chr(3) in r.decode():
                break
        resp.seek(0)

        logger.debug("RESPONSE: %s", resp.getvalue().decode())
        resp.seek(0)
        return resp

    def parse_response(self, response) -> Dict:
        """
        Sends message through socket connection and parses the response into a
        VIFMessage.

        The response may span multiple lines. Each line is treated as a
        separate VIFMessage and this is stored in a dictionary as a list of
        messages under a particular record code.
        """

        # Parse response into dictionary where the key is equal to the record
        # code and the value is a list of VIFMessages
        return_data = defaultdict(list)  # type: Dict[str, List[Dict]]
        for line in response:
            row = line.rstrip().decode().replace(chr(3), '')
            if row[:1] == ';' or len(row) == 0:
                continue  # skip comment
            record = VIFMessage(content=row)
            return_data[record.record_code].append(record.data())
        return return_data

    def send(self, message=None) -> Dict:
        resp = {}  # type: Dict[str, List[Dict]]
        if message:
            message.set_header(**self.gateway_headers)

            logger.debug("REQUEST: %s", message.content)

            # connect to Venue cinema and send message
            message = message.content.encode()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.host, self.DEFAULT_PORT))
            sock.sendall(message)
            response = self.parse_sock(sock)
            sock.close()
        return self.parse_response(response)
