from collections import defaultdict
from typing import Dict, List, Any, Tuple

from .vif_field_map import TICKET_ARRAY_FIELD_MAP, PAYMENT_ARRAY_FIELD_MAP
from .common import swap_schema_field_key


class VIFBaseArray(object):
    FIELD_MAP = None  # type: Dict[str, Dict[int, Tuple]]
    FIELD_SEED = None  # type: int
    FIELD_SEED_MULTIPLIER = None  # type: int

    def __init__(self, record_code, data=None, named_data=None):
        # type: (str, Dict, List) -> None
        self._data = []  # type: List[Dict[int, Any]]
        self.record_code = record_code
        if data is not None:
            self.load_data_into_array(data)
        elif named_data is not None:
            self.load_named_data_into_array(named_data)

    def _extract_array_specific_fields(self, d):
        # type: (Dict) -> Dict
        raise NotImplementedError

    def _create_structured_array(self, d):
        # type: (Dict) -> Dict
        """
        Converts flattened array key structure into nested dictionary

        For example:
        d = {
            100101: 'BOUNT00',
            100103: 5,
            100108: 1,
            100201: 'BOUNT00',
            100203: 5,
            100208: 1,

        Converts to...

        parsed_d = {
            1: {1: 'BOUNT00', 3: 5, 8: 1},
            2: {1: 'BOUNT00', 3: 5, 8: 1},
        }
        """
        parsed_array = defaultdict(dict)  # type: Dict[int, Dict[int, Any]]
        for key, value in d.items():
            item_counter = (int(key) - self.FIELD_SEED) // self.FIELD_SEED_MULTIPLIER
            field_number = (int(key) - self.FIELD_SEED) % self.FIELD_SEED_MULTIPLIER
            parsed_array[item_counter][field_number] = value
        return dict(parsed_array)

    def _convert_named_keys_to_integer(self, data, record_code):
        # type: (Dict, str) -> Dict
        field_map = self.FIELD_MAP.get(record_code)
        reverse_field_map = swap_schema_field_key(field_map)
        parsed_data = {}
        for key, value in data.items():
            field_number, field_type = reverse_field_map[key]
            parsed_data[field_number] = field_type(value)
        return parsed_data

    def load_data_into_array(self, d):
        # type: (Dict) -> None
        array_data = self._extract_array_specific_fields(d)
        structured_array = self._create_structured_array(array_data)
        for _, v in structured_array.items():
            self._data.append(v)

    def load_named_data_into_array(self, d):
        # type: (List) -> None
        for item in d:
            self.add_array_item(**item)

    def add_array_item(self, **kwargs):
        # type: (**Any) -> None
        item = self._convert_named_keys_to_integer(data=kwargs, record_code=self.record_code)
        self._data.append(item)

    def sum_field(self, field):
        # type: (str) -> float
        total = float(0)
        for item in self.friendly_data():
            total += float(item.get(field, 0))
        return total

    def count(self):
        # type: () -> int
        return len(self._data)

    def data(self):
        # type: () -> Dict
        """
        Returns data dictionary with integer keys and values
        in the format specified by the Venue schema
        """
        array = list(enumerate(self._data, start=1))
        data = {}
        field_map = self.FIELD_MAP.get(self.record_code, {})
        for i, item in array:
            item_key = self.FIELD_SEED + i * self.FIELD_SEED_MULTIPLIER
            for key, value in item.items():
                _, field_type = field_map.get(key, (None, lambda x: x))
                data[item_key + key] = field_type(value)
        return data

    def friendly_data(self):
        # type: () -> List[Dict]
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

    def __init__(self, **kwargs):
        # type: (**Any) -> None
        self.FIELD_MAP = TICKET_ARRAY_FIELD_MAP
        self.FIELD_SEED = 100000
        self.FIELD_SEED_MULTIPLIER = 100
        super(VIFTicketArray, self).__init__(**kwargs)

    def _extract_array_specific_fields(self, d):
        # type: (Dict) -> Dict
        return_dict = {}  # type: Dict
        if self.record_code in ('q30', 'p30', 'p31', 'p32'):
            return_dict = dict((k, v) for k, v in d.items() if int(k) > 100100)
        return return_dict

    def total_ticket_prices(self):
        # type: () -> float
        return self.sum_field('ticket_price')

    def total_ticket_fees(self):
        # type: () -> float
        return self.sum_field('ticket_service_fee')

    def total(self):
        # type: () -> float
        return self.total_ticket_prices() + self.total_ticket_fees()

    def add_ticket(self, **kwargs):
        # type: (**Any) -> None
        self.add_array_item(**kwargs)


class VIFPaymentArray(VIFBaseArray):

    def __init__(self, **kwargs):
        # type: (**Any) -> None
        self.FIELD_MAP = PAYMENT_ARRAY_FIELD_MAP
        self.FIELD_SEED = 1000
        self.FIELD_SEED_MULTIPLIER = 100
        super(VIFPaymentArray, self).__init__(**kwargs)

    def _extract_array_specific_fields(self, d):
        # type: (Dict) -> Dict
        return_dict = {}  # type: Dict
        if self.record_code in ('q31',):
            return_dict = dict((k, v) for k, v in d.items() if int(k) > 1100 and int(k) < 2000)
        return return_dict

    def total_amount_paid(self):
        # type: () -> float
        return self.sum_field('amount_paid')

    def add_payment(self, **kwargs):
        # type: (**Any) -> None
        self.add_array_item(**kwargs)

    def add_stripe_payment(self, amount, transaction_id):
        # type: (float, str) -> None
        self.add_payment(payment_category=14, payment_provider='Stripe',
                         amount_paid=amount, transaction_id=transaction_id)

    def add_paypal_payment(self, amount, transaction_id):
        # type: (float, str) -> None
        self.add_payment(payment_category=14, payment_provider='PayPal',
                         amount_paid=amount, transaction_id=transaction_id)


class VIFSeatArray(VIFBaseArray):

    def __init__(self, **kwargs):
        # type: (**Any) -> None
        self.FIELD_MAP = PAYMENT_ARRAY_FIELD_MAP
        self.FIELD_SEED = 1000
        self.FIELD_SEED_MULTIPLIER = 1
        super(VIFSeatArray, self).__init__(**kwargs)

    def _extract_array_specific_fields(self, d):
        # type: (Dict) -> Dict
        return_dict = {}  # type: Dict
        if self.record_code in ('p30', 'p31'):
            return_dict = dict((k, v) for k, v in d.items() if int(k) > 1000 and int(k) < 1100)
        return return_dict

    def friendly_data(self):
        # type: () -> List
        return list(s[0] for s in self._data)
