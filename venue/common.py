from typing import Dict


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
