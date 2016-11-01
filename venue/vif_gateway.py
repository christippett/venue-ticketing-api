import socket
from collections import defaultdict
from io import BytesIO
from random import choice
from string import ascii_uppercase
from typing import Dict

from .vif_message import VIFMessage
from .vif_ticket_array import VIFTicketArray


class VIFGatewayError(Exception):
    pass


class VIFGateway(object):
    DEFAULT_PORT = 4016
    DEFAULT_USERCODE = 'TKTBTY'
    VIFGatewayError = VIFGatewayError

    def __init__(self, host=None, auth_key=None, agent_no=None,
                 site_name=None):
        self.host = host
        self.auth_key = auth_key
        self.agent_no = agent_no
        self.site_name = site_name
        self.message_history = {}

    def random_pattern(self, length: int) -> str:
        return ''.join(choice(ascii_uppercase) for i in range(length))

    def create_message(self, **kwargs) -> VIFMessage:
        default_header = {
            'record_code': 'vrq',
            'site_name': self.site_name,
            'packet_id': self.random_pattern(4),
            'request_code': None,
            'comment': 'Ticket Bounty VIF Gateway v0.1',
            'auth_info': "%s%s" % (self.auth_key, self.agent_no),
            'gateway_type': 0
        }
        for key, value in kwargs.items():
            default_header[key] = value
        return VIFMessage(**default_header)

    def parse_response(self, sock, size=8192) -> Dict:
        """
        Sends message through socket connection and parses the response into a
        VIFMessage.

        The response may span multiple lines. Each line is treated as a
        separate VIFMessage and this is stored in a dictionary as a list of
        messages under a particular record code.
        """
        # Write response to stream
        resp = BytesIO()
        while True:
            r = sock.recv(size)
            resp.write(r)
            if chr(3) in r.decode():
                break
        resp.seek(0)

        # Parse response into dictionary where the key is equal to the record
        # code and the value is a list of VIFMessages
        return_data = defaultdict(list)  # type: Dict[str, List[Dict]]
        for line in resp:
            row = line.rstrip().decode().replace(chr(3), '')
            if row[:1] == ';' or len(row) == 0:
                continue  # skip comment
            record = VIFMessage(content=row)
            return_data[record.record_code].append(record.data())
        return return_data

    def send(self, message=None) -> Dict:
        resp = {}  # type: Dict[str, List[Dict]]
        if message:
            self.message_history[
                message.header_dict(get_field_names=True)['packet_id']] = message
            message = message.content.encode()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.host, self.DEFAULT_PORT))
            sock.sendall(message)
            resp = self.parse_response(sock)
            sock.close()
        return resp

    def handshake(self) -> Dict:
        message = self.create_message(request_code=1)
        return self.send(message)

    def get_data(self, detail_required=2) -> Dict:
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
        body = {'1': detail_required}
        message = self.create_message(request_code=2, body=body)
        return self.send(message)

    def verify_booking(self, alt_booking_key=None) -> Dict:
        """
        Record code: 42
        Description: Returns key information about a booking if the booking is
            still current, otherwise an error is returned.
        """
        body = {'1': alt_booking_key}
        message = self.create_message(request_code=42, body=body)
        return self.send(message)

    def get_session_seats(self, session_no=None, availability='0') -> Dict:
        """
        Record code: 20
        Description: Can be used to retrieve a snapshot of the current seating
            status for the specified session.
        Availability:
            0=Get All Seats
            1=Available
            2=Unavailable
        """
        body = {'1': session_no, '2': availability}
        message = self.create_message(request_code=20, body=body)
        return self.send(message)

    def init_transaction(self, workstation_id=None, user_code=None,
                         session_no=None, transaction_type=1,
                         customer_reference=None,
                         ticket_array=VIFTicketArray()) -> Dict:
        """
        Record code: 30
        Description: This request will cause an “init” internet booking to be
            recorded. That is, it will commence a booking transaction and
            tickets will be reserved. The transaction will remain incomplete
            until the client application performs a “Commit Internet Booking”.
        Body: q30 record
        Response: p30 record
        """
        user_code = user_code or self.DEFAULT_USERCODE
        body = {
            '1': workstation_id,      # workstation id
            '2': user_code,           # user code
            '3': session_no,          # session number
            '4': transaction_type,    # transaction type (1=paid booking)
            '5': customer_reference,  # customer reference
            '10': ticket_array.total_ticket_prices(),  # total ticket price
            '11': ticket_array.total_ticket_fees(),    # total ticket fees
            # '12': '',                  # transaction service fee
            '13': ticket_array.total(),  # total transaction price
            # '14': '',                  # total rainout amount
            # '15': '',                  # loyalty card number
            # '16': ''                   # booking notes
            '100001': ticket_array.count()
        }
        body.update(ticket_array.dict())
        message = self.create_message(request_code=30, body=body)
        return self.send(message)

    def commit_transaction(self, session_no=None) -> Dict:
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
        body = {
            '1': 'workstation id'
        }
        message = self.create_message(request_code=30, body=body)
        return self.send(message)
