import re
from collections import OrderedDict
from typing import Dict

from .vif_field_map import VIF_FIELD_MAP
from .vif_ticket_array import VIFTicketArray
from .common import reverse_field_lookup


class VIFRecord(object):
    TERM_KEY = chr(3)
    COMMENT_KEY = ';'
    HEADER_PATTERN = r'(?:\{(?P<record_code>.{3})\})(?=\{|$)'
    KEY_VALUE_PATTERN = r'(?:\{(?P<key>\d+)\}(?P<value>.*?))(?=\{|$)'

    def __init__(self, record_code: str=None, raw_content: str=None,
                 data: Dict=None):
        self.data = {}
        self.raw_content = raw_content
        self.record_code = record_code

        if raw_content:
            self.record_code = self._extract_record_code_from_raw_content(raw_content)
            self.data = self._parse_raw_content(raw_content)
        elif data:
            integer_key_count = self._count_integer_keys(data)
            if integer_key_count == 0:
                self.data = self._map_named_keys_to_integer(data, record_code)
            else:
                self.data = data

    def _extract_record_code_from_raw_content(self, raw_content: str) -> str:
        record_code = ''
        match = re.search(self.HEADER_PATTERN, raw_content)
        if match:
            record_code = match.group('record_code')
        return record_code

    def _parse_raw_content(self, raw_content: str) -> Dict:
        data = {}
        key_value_matches = re.compile(self.KEY_VALUE_PATTERN)
        for match in key_value_matches.finditer(raw_content):
            payload = match.groupdict()
            data[int(payload['key'])] = payload['value']
        return data

    def _count_integer_keys(self, d: Dict) -> int:
        count = 0
        for key in d.keys():
            if isinstance(key, int):
                count += 1
        return count

    def _map_named_keys_to_integer(self, data: Dict, record_code: str) -> Dict:
        field_map = VIF_FIELD_MAP.get(record_code)
        reverse_field_map = reverse_field_lookup(field_map)
        parsed_data = {}
        for key, value in data.items():
            integer_field = reverse_field_map.get(key, None)
            if integer_field is not None:
                parsed_data[integer_field] = value
            else:
                raise ValueError
        return parsed_data

    def content(self) -> str:
        """
        Unwraps dictionary key and values into the following format:
        assert format({'key': 'value'}) == "{key}value"
        """
        key_value_pairs = []

        # Order values based on key
        d = OrderedDict(sorted(
            self.data.items(), key=lambda t: t[0]))
        for key, value in d.items():
            key_value_pairs.append("{{{0}}}{1}".format(key, value))

        # Prefix content with record code if available
        formatted_record_code = ''
        if self.record_code:
            formatted_record_code = '{{{0}}}'.format(self.record_code)

        return formatted_record_code + ''.join(key_value_pairs)

    def format_data(self) -> Dict:
        field_map = VIF_FIELD_MAP.get(self.record_code)
        formatted_data = {}
        for key, value in self.data.items():
            field_name = field_map.get(key, 'UNKNOWN_%s' % (key))
            formatted_data[field_name] = value
        return formatted_data
