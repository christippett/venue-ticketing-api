import re
from collections import OrderedDict
from typing import Dict, List, Any

from .vif_field_map import VIF_FIELD_MAP
from .vif_ticket_array import VIFTicketArray, VIFPaymentArray, VIFSeatArray
from .common import swap_schema_field_key, count_integer_keys


class VIFRecord(object):
    TERM_KEY = chr(3)
    COMMENT_KEY = ';'
    HEADER_PATTERN = r'(?:\{(?P<record_code>.{3})\})(?=\{|$)'
    KEY_VALUE_PATTERN = r'(?:\{(?P<key>\d+)\}(?P<value>.*?))(?=\{|$|\r)'
    FIELD_MAP = VIF_FIELD_MAP

    def __init__(self, record_code: str=None, raw_content: str=None,
                 data: Dict=None) -> None:
        self._data = {}  # type: Dict[int, Any]
        self.raw_content = raw_content
        self.record_code = record_code

        if raw_content:
            # Parse Venue's key/value text into an integer key dictionary
            data = self._parse_raw_content(raw_content)
            self.record_code = self._extract_record_code(raw_content)

        # Now that record_code has been defined (either as a constructor variable
        # or from parsing raw_content), we can instantiate the array classes
        self._tickets = VIFTicketArray(record_code=self.record_code)
        self._payments = VIFPaymentArray(record_code=self.record_code)
        self._reserved_seats = VIFSeatArray(record_code=self.record_code)

        if data:
            integer_key_count = count_integer_keys(data)

            # Data uses named keys
            if integer_key_count == 0 and self.record_code is not None:
                # Pop ticket data so it's excluded from subsequent parsing
                ticket_data = data.pop('tickets', [])  # type: List
                self._tickets.load_named_data_into_array(ticket_data)
                # Pop payment data so it's excluded from subsequent parsing
                payment_data = data.pop('payments', [])  # type: List
                self._payments.load_named_data_into_array(payment_data)
                # Convert leftover data to use integer keys
                self._data = self._convert_named_keys_to_integer(data, record_code)

            # Data uses named keys but no record code provided
            elif integer_key_count == 0 and record_code is None:
                # Raise error because we have no way of parsing the named keys
                raise Exception

            # Data may be a mix of integer and named keys (though should be just integer keys)
            else:
                self._data = data
                self._tickets.load_data_into_array(self._data)
                self._payments.load_data_into_array(self._data)
                self._reserved_seats.load_data_into_array(self._data)

        # Overwrite data with processed array data
        self._data.update(self._tickets.data())
        self._data.update(self._payments.data())
        self._data.update(self._reserved_seats.data())

    def _extract_record_code(self, raw_content: str) -> str:
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

    def _convert_named_keys_to_integer(self, data: Dict[str, Any], record_code: str) -> Dict[int, Any]:
        field_map = self.FIELD_MAP[record_code]  # schema _must_ exist for record code
        # Swap integer key for field name
        reverse_field_map = swap_schema_field_key(field_map)
        parsed_data = {}
        for key, value in data.items():
            field_number, field_type = reverse_field_map[key]
            parsed_data[field_number] = field_type(value)
        return parsed_data

    def content(self) -> str:
        """
        Unwraps dictionary key and values into the following format:
        assert format({'key': 'value'}) == "{key}value"
        """
        key_value_pairs = []  # type: List

        # Update aggregate fields
        self._update_aggregate_fields()

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

    def ticket_array(self) -> VIFTicketArray:
        ticket_array = VIFTicketArray(record_code=self.record_code, data=self._data)
        # Only update ticket aggregate fields on request (q30)
        # We trust the server response (p30, p31) to return these values accurately
        if ticket_array.count() > 0 and self.record_code == 'q30':
            transaction_fee = self._data.get(12, 0.0)  # 12=transaction_service_fee
            self._data.update({
                10: ticket_array.total_ticket_prices(),
                11: ticket_array.total_ticket_fees(),
                13: ticket_array.total() + transaction_fee,
                100001: ticket_array.count()
            })
        self._data.update(ticket_array.data())
        return ticket_array

    def payment_array(self) -> VIFPaymentArray:
        payment_array = VIFPaymentArray(record_code=self.record_code, data=self._data)
        # Only update payment aggregate fields on request (q31)
        if payment_array.count() > 0 and self.record_code == 'q31':
            self._data.update({
                4: payment_array.total_amount_paid(),
                100001: payment_array.count()
            })
        self._data.update(payment_array.data())
        return payment_array

    def seat_array(self) -> VIFSeatArray:
        return VIFSeatArray(record_code=self.record_code, data=self._data)

    def exclude_array_data(self) -> Dict[int, Any]:
        return dict((k, v) for k, v in self._data.items() if k < 1000)

    def _update_aggregate_fields(self) -> None:
        if self._tickets.count() > 0 and self.record_code == 'q30':
            transaction_fee = self._data.get(12, 0.0)  # 12=transaction_service_fee
            self._data.update({
                10: self._tickets.total_ticket_prices(),
                11: self._tickets.total_ticket_fees(),
                13: self._tickets.total() + transaction_fee,
                100001: self._tickets.count()
            })
        if self._payments.count() > 0 and self.record_code == 'q31':
            self._data.update({
                4: self._payments.total_amount_paid(),
                100001: self._payments.count()
            })

    def array_keys(self) -> List:
        ticket_keys = list(self._tickets.data().keys())
        payment_keys = list(self._payments.data().keys())
        seat_keys = list(self._reserved_seats.data().keys())
        return list(set(ticket_keys + payment_keys + seat_keys))

    def data(self) -> Dict[int, Any]:
        """
        Returns data dictionary with integer keys and values
        in the format specified by the Venue schema
        """
        data = {}

        # Update aggregate fields
        self._update_aggregate_fields()

        # Convert values to their data type according to the schema
        field_map = self.FIELD_MAP.get(self.record_code, {})
        for key, value in self._data.items():
            _, field_type = field_map.get(key, (None, lambda x: x))
            if key not in self.array_keys():
                data[key] = field_type(value)

        data.update(self._tickets.data())
        data.update(self._payments.data())
        data.update(self._reserved_seats.data())

        return data

    def friendly_data(self) -> Dict[str, Any]:
        formatted_data = {}

        # Update aggregate fields
        self._update_aggregate_fields()

        # Convert integer keys to their mapped field name
        # Convert values to their data type according to the schema
        field_map = self.FIELD_MAP.get(self.record_code, {})
        for key, value in self._data.items():
            # field_name, field_type = field_map.get(key, ('UNKNOWN_%s' % (key), str))
            field_name, field_type = field_map.get(key, (str(key), str))
            if key not in self.array_keys():
                formatted_data[field_name] = field_type(value)

        if self._tickets.count() > 0:
            formatted_data.update({'tickets': self._tickets.friendly_data()})
        if self._payments.count() > 0:
            formatted_data.update({'payments': self._payments.friendly_data()})
        if self._reserved_seats.count() > 0:
            formatted_data.update({'reserved_seats': self._reserved_seats.friendly_data()})

        return formatted_data
