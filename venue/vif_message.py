import re
from collections import defaultdict
from typing import Any, Dict, List, Tuple, TypeVar

from .common import generate_pattern
from .vif_record import VIFRecord

T = TypeVar('T', bound='VIFMessage')


class VIFMessage(object):
    term_key = chr(3)
    comment_key = ';'
    MESSAGE_PATTERN = r'^(?P<header>\{.+?\}.*?)!(?P<body>.*?)(?:$|'+chr(3)+')'  # dotline
    VIF_RECORD_PATTERN = r'^(?!;)(?P<vif_record>\{.+\}.*)$'  # multiline

    def __init__(self, content: str=None) -> None:
        if content is not None:
            # Parse text contents into data
            self.header_content, self.body_content = self._extract_content(content)
            self.header = VIFRecord(raw_content=self.header_content)
            self.body = self._parse_body_content(self.body_content)
        else:
            # Initiate empty message (data needs to be added later)
            self.header_content = None
            self.body_content = None
            self.header = None
            self.body = []

    def _extract_content(self, content: str) -> Tuple:
        pattern = re.compile(self.MESSAGE_PATTERN, re.DOTALL)
        match = pattern.match(content)
        if match:
            header = match.group('header')
            body = match.group('body')
            return (header, body)
        else:
            raise Exception  # content doesn't conform to pattern

    def _parse_body_content(self, content: str) -> List:
        body = []
        pattern = re.compile(self.VIF_RECORD_PATTERN, re.MULTILINE)
        for match in pattern.finditer(content):
            body_content = match.group(1)
            record = VIFRecord(raw_content=body_content)
            body.append(record)
        return body

    def content(self) -> str:
        body_content = [record.content() for record in self.body]
        header_content = self.header.content()
        return header_content + '!' + '\n'.join(body_content)

    def set_request_header(self, request_code: int, **kwargs) -> None:
        header_data = {
            'site_name': kwargs.get('site_name'),
            'packet_id': kwargs.get('packet_id', generate_pattern(4)),
            'request_code': request_code,
            'comment': kwargs.get('comment', 'Ticket Bounty VIF Gateway v0.1'),
            'auth_info': kwargs.get('auth_info'),
            'gateway_type': kwargs.get('gateway_type', 0)  # 0=Ticketing, 1=Concessions, 2=Voucher
        }
        self.header = VIFRecord(record_code='vrq', data=header_data)

    def add_body_record(self, body_record: VIFRecord) -> None:
        self.body.append(body_record)

    def header_data(self) -> Dict[str, Any]:
        return self.header.friendly_data()

    def _consolidate_data_dictionary(self, d: Dict) -> Dict:
        for key, value in d.items():
            if len(value) == 1:
                d[key] = value[0]
        return d

    def friendly_data(self) -> Dict:
        record_list = defaultdict(list)
        # Get body records
        for record in self.body:
            record_list[record.record_code].append(record.friendly_data())
        # Get header record
        record_list[self.header.record_code].append(self.header.friendly_data())
        return self._consolidate_data_dictionary(dict(record_list))

    def data(self) -> Dict:
        record_list = defaultdict(list)
        # Get body records
        for record in self.body:
            record_list[record.record_code].append(record.data())
        # Get header record
        record_list[self.header.record_code].append(self.header.friendly_data())
        return self._consolidate_data_dictionary(dict(record_list))
