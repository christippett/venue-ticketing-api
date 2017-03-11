import re
from collections import OrderedDict
from typing import Dict, List

from .vif_field_map import VIF_FIELD_MAP
from .vif_ticket_array import VIFTicketArray
from .common import swap_schema_field_key, count_integer_keys


class VIFRecord(object):
    TERM_KEY = chr(3)
    COMMENT_KEY = ';'
    HEADER_PATTERN = r'(?:\{(?P<record_code>.{3})\})(?=\{|$)'
    KEY_VALUE_PATTERN = r'(?:\{(?P<key>\d+)\}(?P<value>.*?))(?=\{|$)'
    FIELD_MAP = VIF_FIELD_MAP

    def __init__(self, record_code: str=None, raw_content: str=None,
                 data: Dict=None):
        self._data = {}
        self.raw_content = raw_content
        self.record_code = record_code

        if raw_content:
            self.record_code = self._extract_record_code_from_raw_content(raw_content)
            self._data = self._parse_raw_content(raw_content)
        elif data:
            integer_key_count = count_integer_keys(data)
            if integer_key_count == 0:
                ticket_data = data.pop('tickets', [])  # type: List
                self._data = self._parse_data_with_named_keys(data, record_code)
                if len(ticket_data) > 0:
                    self._data.update(self._parse_ticket_data_with_named_keys(ticket_data))
            else:
                self._data = data

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

    def _parse_data_with_named_keys(self, data: Dict, record_code: str) -> Dict:
        field_map = self.FIELD_MAP[record_code]  # schema _must_ exist for record code
        reverse_field_map = swap_schema_field_key(field_map)
        parsed_data = {}
        for key, value in data.items():
            field_number, field_type = reverse_field_map[key]
            parsed_data[field_number] = field_type(value)
        return parsed_data

    def _parse_ticket_data_with_named_keys(self, ticket_data: List) -> Dict:
        ticket_array = VIFTicketArray(record_code=self.record_code)
        for ticket in ticket_data:
            ticket_array.add_ticket(**ticket)
        return ticket_array.data()

    def _extract_ticket_data(self, data: Dict) -> Dict:
        return dict((k, v) for k, v in data.items() if int(k) > 100001)

    def content(self) -> str:
        """
        Unwraps dictionary key and values into the following format:
        assert format({'key': 'value'}) == "{key}value"
        """
        key_value_pairs = []

        # Order values based on key
        d = OrderedDict(sorted(
            self._data.items(), key=lambda t: t[0]))
        for key, value in d.items():
            key_value_pairs.append("{{{0}}}{1}".format(key, value))

        # Prefix content with record code if available
        formatted_record_code = ''
        if self.record_code:
            formatted_record_code = '{{{0}}}'.format(self.record_code)

        return formatted_record_code + ''.join(key_value_pairs)

    def ticket_array(self):
        ticket_data = self._extract_ticket_data(self._data)
        return VIFTicketArray(record_code=self.record_code, ticket_array=ticket_data)

    def data_excluding_arrays(self):
        ticket_data = self._extract_ticket_data(self._data)
        return dict((k, v) for k, v in self._data.items() if k not in ticket_data.keys())

    def data(self):
        """
        Returns data dictionary with integer keys and values
        in the format specified by the Venue schema
        """
        # Extract keys relating to ticket array
        data = self.data_excluding_arrays()

        field_map = self.FIELD_MAP.get(self.record_code, {})
        for key, value in data.items():
            field_name, field_type = field_map.get(key, (None, lambda x: x))
            data[key] = field_type(value)

        # Add ticket data if present
        ticket_array = self.ticket_array()
        if ticket_array.count() > 0:
            data.update(ticket_array.data())

        return data

    def friendly_data(self) -> Dict:
        formatted_data = {}

        # Extract keys relating to ticket array
        data = self.data_excluding_arrays()

        field_map = self.FIELD_MAP.get(self.record_code, {})
        for key, value in data.items():
            field_name, field_type = field_map.get(key, ('UNKNOWN_%s' % (key), str))
            formatted_data[field_name] = field_type(value)

        # Add ticket friendly data if present
        ticket_array = self.ticket_array()
        if ticket_array.count() > 0:
            formatted_data.update({'tickets': ticket_array.friendly_data()})

        return formatted_data
