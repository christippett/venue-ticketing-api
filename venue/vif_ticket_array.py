from collections import defaultdict
from typing import Dict, List, Any

from .vif_field_map import TICKET_ARRAY_FIELD_MAP, PAYMENT_ARRAY_FIELD_MAP
from .common import swap_schema_field_key


class VIFBaseArray(object):
    FIELD_MAP = None

    def __init__(self, record_code: str, array: Dict=None) -> None:
        self._data = []  # type: List[Dict[int, Any]]
        self.record_code = record_code
        if array is not None:
            parsed_array = self._parse_array(
                self._extract_fields_from_array(array)
            )
            self._load_items_from_array(parsed_array)

    def _extract_fields_from_array(self, d: Dict) -> Dict:
        return dict((k, v) for k, v in d.items() if int(k) > 100001)

    def _parse_array(self, d: Dict) -> Dict:
        parsed_array = defaultdict(dict)  # type: Dict[int, Dict[int, Any]]
        for key, value in d.items():
            ticket_counter = (int(key) - 100000) // 100
            field_number = (int(key) - 100000) % 100
            parsed_array[ticket_counter][field_number] = value
        return dict(parsed_array)

    def _load_items_from_array(self, d: Dict) -> None:
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

    def add_array_item(self, **kwargs) -> None:
        ticket = self._parse_data_with_named_keys(data=kwargs, record_code=self.record_code)
        self._data.append(ticket)

    def count(self) -> int:
        return len(self._data)

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
                # field_name, field_type = field_map.get(key, ('UNKNOWN_%s' % (key), str))
                field_name, field_type = field_map.get(key, (str(key), str))
                formatted_data[field_name] = field_type(value)
            array_items.append(formatted_data)
        return array_items


class VIFTicketArray(VIFBaseArray):
    FIELD_MAP = TICKET_ARRAY_FIELD_MAP

    def _extract_fields_from_array(self, d: Dict) -> Dict:
        return dict((k, v) for k, v in d.items() if int(k) > 100001)

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

    def add_ticket(self, **kwargs) -> None:
        return self.add_array_item(**kwargs)


class VIFPaymentArray(VIFBaseArray):
    FIELD_MAP = PAYMENT_ARRAY_FIELD_MAP

    def _extract_fields_from_array(self, d: Dict) -> Dict:
        return dict((k, v) for k, v in d.items() if int(k) > 1000 and int(k) < 100000)

    def add_ticket(self, **kwargs) -> None:
        return self.add_array_item(**kwargs)
