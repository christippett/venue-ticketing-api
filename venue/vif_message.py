import re
from collections import OrderedDict
from typing import Dict

from .vif_field_map import VIF_FIELD_MAP
from .vif_ticket_array import VIFTicketArray


class VIFBaseMessage(object):
    term_key = chr(3)
    comment_key = ';'

    def __init__(self, record_code=None, content=None, **kwargs):
        self._header = {}
        self._body = {}
        self.record_code = 'empty'

        if not record_code and not content:
            return  # empty VIFMessage instance

        if content:
            d = self.content_to_dict(content)
            self._body = d['body']
            self._header = d['header']
            self._content = content
        else:
            self.set_record_code(record_code)
            self._body = kwargs.pop('body', {})
            self.set_header(**kwargs)

    def set_header(self, **kwargs) -> None:
        for key, value in kwargs.items():
            integer_field = self._english_fields.get(key)
            if integer_field:
                self._header[integer_field] = value
            else:
                raise KeyError("'%s' not a valid key for record code '%s'"
                               % (key, self.record_code))

    def set_record_code(self, record_code: str) -> None:
        """
        Get mapping between the numbered field and its english definition
        depending on the message's record code
        """
        self.record_code = record_code or 'err'
        self._integer_fields = VIF_FIELD_MAP.get(self.record_code)
        self._english_fields = self.reverse_field_lookup(self._integer_fields)

    def reverse_field_lookup(self, d: Dict) -> Dict:
        """
        Reverses key/value pair in a dictionary. E.g.
            x = {
                '1': 'Field A',
                '2': 'Field B',
                '3': 'Field C'
            }

        Becomes...
            x = {
                'Field A': '1',
                'Field B': '2',
                'Field C': '3'
            }
        """
        return_dict = {}
        for key, value in d.items():
            return_dict[value] = key
        return return_dict

    def content_to_dict(self, content: str) -> Dict:
        """
        Converts raw message response from VIF Gateway into separate Python
        dictionaries with the message headers and body as key/value pairs
        """
        header_pattern = re.compile(r'^\{(?P<record_code>.{3})\}.*')
        header_match = header_pattern.match(content)
        if header_match:
            record_code = header_match.group('record_code')
            self.set_record_code(record_code)

        if self.record_code in ('vrq', 'vrp'):
            # content could contain body
            pattern = re.compile(r'^\{(?:.{3})\}'
                                 r'(?P<header>.*?)'
                                 r'(?:!(?=\{)(?P<body>.*?))?'
                                 r'(?:!;?)?(?:' + self.term_key + ')?$')
        else:
            # no body, treat all exclamation marks as part of the content
            pattern = re.compile(r'^\{(?:.{3})\}'
                                 r'(?P<header>.*?)'
                                 r'(?P<body>)'
                                 r'(?:!;?)?(?:' + self.term_key + ')?$')

        payload_pattern = re.compile(r'(?:\{(?P<key>\d+)\}'
                                     r'(?P<value>.*?))(?=\{|$)')
        pattern_match = pattern.match(content)
        if pattern_match:
            header_content = pattern_match.group('header')
            body_content = pattern_match.group('body')
            header = {}
            body = {}
            if header_content:
                for match in payload_pattern.finditer(header_content):
                    payload = match.groupdict()
                    header[payload['key']] = payload['value']
            if body_content:
                for match in payload_pattern.finditer(body_content):
                    payload = match.groupdict()
                    body[payload['key']] = payload['value']

            return {
                'body': body,
                'header': header
            }

    def format_vif_message(self, d: Dict) -> str:
        """
        Unwraps dictionary key and values into the following format:
        assert format({'key': 'value'}) == "{key}value"
        """
        payload = []
        # Order parameters based on key
        d = OrderedDict(sorted(
            d.items(), key=lambda t: int(t[0]) if t[0].isdigit() else 0))
        for key, value in d.items():
            payload.append("{{{0}}}{1}".format(key, value))
        return ''.join(payload)

    def header(self) -> str:
        return "{%s}%s" % (self.record_code,
                           self.format_vif_message(d=self._header))

    def header_dict(self, get_field_names: bool=False) -> Dict:
        if get_field_names:
            field_names = {}
            # Get integer that maps to key value
            for key, value in self._header.items():
                integer_key = self._integer_fields. \
                    get(key, 'UNKNOWN_%s' % (key))
                field_names[integer_key] = value
            return field_names
        else:
            return self._header

    def body(self) -> str:
        return self.format_vif_message(self._body)

    def body_dict(self) -> Dict:
        return {} or self._body

    def data(self, get_field_names: bool=True) -> Dict:
        return {
            'header': self.header_dict(get_field_names=get_field_names),
            'body': self.body_dict()
        }

    @property
    def content(self) -> str:
        if self._body:
            content = "{header}!{body}{termkey}"
        else:
            content = "{header}{termkey}"
        return content.format(header=self.header(),
                              body=self.body(),
                              termkey=self.term_key)

    @content.setter
    def content(self, content: str) -> None:
        self.content_to_dict(content)

    def __str__(self) -> str:
        return self.content

    def __repr__(self) -> str:
        return "<'%s' record>" % (self.record_code)


class VIFMessage(VIFBaseMessage):
    @classmethod
    def _create_request(cls, **kwargs):
        return cls(record_code='vrq', **kwargs)

    @classmethod
    def handshake(cls) -> Dict:
        return cls._create_request(request_code=1)

    @classmethod
    def get_data(cls, detail_required: int=2) -> Dict:
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
        return cls._create_request(request_code=2, body=body)

    @classmethod
    def verify_booking(cls, alt_booking_key: str) -> Dict:
        """
        Record code: 42
        Description: Returns key information about a booking if the booking is
            still current, otherwise an error is returned.
        """
        body = {'1': alt_booking_key}
        return cls._create_request(request_code=42, body=body)

    @classmethod
    def get_session_seats(cls, session_no: int, availability: int=0) -> Dict:
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
        return cls._create_request(request_code=20, body=body)

    @classmethod
    def init_transaction(cls, workstation_id: int, user_code: str,
                         session_no: int, customer_reference: str,
                         ticket_array: VIFTicketArray, transaction_type: int=1,) -> Dict:
        """
        Record code: 30
        Description: This request will cause an “init” internet booking to be
            recorded. That is, it will commence a booking transaction and
            tickets will be reserved. The transaction will remain incomplete
            until the client application performs a “Commit Internet Booking”.
        Body: q30 record
        Response: p30 record

        Example request:
            {vrq}{1}BARKER{2}6A85{3}30{4}Ticket Bounty{5}3{8}108193016648!
            {1}627{2}VifTest{3}132417{4}1{11}2{12}15{13}37{100001}2
            {100101}BOUNT00{100102}10{100103}1{100104}A13
            {100201}BOUNT00{100202}10{100203}1{100204}A14{10}20

        Example response:
            {vrp}{1}BARKER{2}6A85!
            {p30}{3}Cinema 02{4}Cinema Two{5}MOANA{6}Moana{7}20170110100000{8}15{9}2{10}37{1001}A 14{1002}A 13{100001}2
            {100101}BOUNT00{100103}10{100105}A 14{100106}Tkt Bounty Web{100108}1
            {100201}BOUNT00{100203}10{100205}A 13{100206}Tkt Bounty Web{100208}1
        """
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
        return cls._create_request(request_code=30, body=body)

    def commit_transaction(self, workstation_id: int, total_paid: float,
                           booking_key: str) -> Dict:
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
            '2': workstation_id,
            '4': total_paid,
            '5': booking_key,  # mandatory
            '7': '0417070155',  # customer phone number
            '11': 'WWW',  # origin
            '1001': 1,  # hard code only one payment
            '1101': 14,  # micropayment
            '1102': 'Ticket Bounty',
            '1103': total_paid,
        }
        return self._create_request(request_code=31, body=body)

