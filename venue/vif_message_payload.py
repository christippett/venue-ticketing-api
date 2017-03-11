import re
from collections import OrderedDict
from typing import Dict, List, Tuple

from .vif_field_map import VIF_FIELD_MAP
from .vif_ticket_array import VIFTicketArray
from .vif_record import VIFRecord
from .common import reverse_field_lookup


class VIFMessagePayload(object):
    term_key = chr(3)
    comment_key = ';'
    MESSAGE_PATTERN = r'^(?P<header>\{.+?\}.*?)!(?P<body>.*)$'  # dotline
    VIF_RECORD_PATTERN = r'^(?!;)(?P<vif_record>\{.+\}.*)$'  # multiline

    def __init__(self, content: str=None):
        self.header_content, self.body_content = self._extract_content(content)
        self.header = VIFRecord(raw_content=self.header_content)
        self.body = self._parse_body_content(self.body_content)

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

    def content(self):
        body_content = [record.content() for record in self.body]
        header_content = self.header.content()
        return header_content + '!' + '\n'.join(body_content)



