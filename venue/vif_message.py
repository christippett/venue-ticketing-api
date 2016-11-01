import re
from collections import OrderedDict
from typing import Dict

from .vif_field_map import VIF_FIELD_MAP


class VIFMessage(object):
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
            if kwargs.get('body'):
                self._body = kwargs.pop('body')
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
