from collections import defaultdict
from typing import Dict, List, Any

from .vif_field_map import TICKET_ARRAY_FIELD_MAP
from .common import swap_schema_field_key


class VIFTicketArray(object):
    FIELD_MAP = TICKET_ARRAY_FIELD_MAP

    def __init__(self, record_code: str, ticket_array: Dict=None) -> None:
        self._data = []  # type: List[Dict[int, Any]]
        self.record_code = record_code
        if ticket_array is not None:
            parsed_ticket_array = self._parse_ticket_array(
                self._extract_ticket_fields_from_array(ticket_array)
            )
            self._load_tickets_from_array(parsed_ticket_array)

    def _extract_ticket_fields_from_array(self, d: Dict) -> Dict:
        return dict((k, v) for k, v in d.items() if int(k) > 100000)

    def _parse_ticket_array(self, d: Dict) -> Dict:
        parsed_ticket_array = defaultdict(dict)  # type: Dict[int, Dict[int, Any]]
        for key, value in d.items():
            ticket_counter = (int(key) - 100000) // 100
            field_number = (int(key) - 100000) % 100
            parsed_ticket_array[ticket_counter][field_number] = value
        return dict(parsed_ticket_array)

    def _load_tickets_from_array(self, d: Dict):
        for k, v in d.items():
            self._data.append(v)

    def _parse_data_with_named_keys(self, data: Dict, record_code: str) -> Dict:
        field_map = self.FIELD_MAP.get(record_code)
        reverse_field_map = swap_schema_field_key(field_map)
        parsed_data = {}
        for key, value in data.items():
            field_number, field_type = reverse_field_map[key]
            parsed_data[field_number] = field_type(value)
        return parsed_data

    def add_ticket(self, **kwargs) -> None:
        ticket = self._parse_data_with_named_keys(data=kwargs, record_code=self.record_code)
        self._data.append(ticket)

    def count(self) -> int:
        return len(self._data)

    def _total_ticket_field(self, field) -> float:
        total = float(0)
        for ticket in self.friendly_data():
            total += float(ticket.get(field, 0))
        return total

    def total_ticket_prices(self) -> float:
        return self._total_ticket_field('ticket_price')

    def total_ticket_fees(self) -> float:
        return self._total_ticket_field('ticket_service_fee')

    def total(self) -> float:
        return self.total_ticket_prices() + self.total_ticket_fees()

    def data(self) -> Dict:
        """
        Returns data dictionary with integer keys and values
        in the format specified by the Venue schema
        """
        array = list(enumerate(self._data, start=1))
        data = {}
        field_map = self.FIELD_MAP.get(self.record_code, {})
        for i, ticket in array:
            ticket_key = 100000 + i * 100
            for key, value in ticket.items():
                field_name, field_type = field_map.get(key, (None, lambda x: x))
                data[ticket_key + key] = field_type(value)
        return data

    def friendly_data(self) -> List[Dict]:
        array_items = []
        field_map = self.FIELD_MAP.get(self.record_code, {})
        for array_item in self._data:
            formatted_data = {}
            for key, value in array_item.items():
                field_name, field_type = field_map.get(key, ('UNKNOWN_%s' % (key), str))
                formatted_data[field_name] = field_type(value)
            array_items.append(formatted_data)
        return array_items
