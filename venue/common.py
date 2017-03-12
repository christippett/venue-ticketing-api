import uuid
from datetime import datetime
from typing import Dict


def format_datetime(value):
    # 20150625095222
    return datetime.strptime(value, '%Y%m%d%H%M%S')


def generate_pattern(length: int) -> str:
    return str(uuid.uuid4()).upper()[:length]


def reverse_field_lookup(d: Dict) -> Dict:
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


def swap_schema_field_key(d: Dict) -> Dict:
    """
    Reverses key/value pair of field mapping schema
        x = {
            1: ('field_a', str),
            2: ('field_b', str),
            3: ('field_c', int)
        }

    Becomes...
        x = {
            'field_a': (1, str),
            'field_b': (2, str),
            'field_c': (3, int)
        }
    """
    return_dict = {}
    for key, value in d.items():
        field_name, field_type = value
        return_dict[field_name] = (key, field_type)
    return return_dict


def count_integer_keys(d: Dict) -> int:
    count = 0
    for key in d.keys():
        if isinstance(key, int):
            count += 1
    return count
