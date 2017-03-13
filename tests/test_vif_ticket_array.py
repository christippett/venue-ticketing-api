import pytest

from venue.vif_ticket_array import VIFTicketArray


def test_count_ticket_array():
    ticket_array = VIFTicketArray(record_code='q30')
    ticket_array.add_ticket(ticket_code='BOUNT00', ticket_price=5, ticket_service_fee=1)
    ticket_array.add_ticket(ticket_code='BOUNT00', ticket_price=5, ticket_service_fee=1)
    ticket_array.add_ticket(ticket_code='BOUNT00', ticket_price=5, ticket_service_fee=1)

    assert ticket_array.count() == 3


def test_sum_ticket_prices():
    ticket_array = VIFTicketArray(record_code='q30')
    ticket_array.add_ticket(ticket_code='BOUNT00', ticket_price=5, ticket_service_fee=1)
    ticket_array.add_ticket(ticket_code='BOUNT00', ticket_price=5, ticket_service_fee=1)
    ticket_array.add_ticket(ticket_code='BOUNT00', ticket_price=5, ticket_service_fee=1)

    assert ticket_array.total_ticket_prices() == 15


def test_sum_ticket_fees():
    ticket_array = VIFTicketArray(record_code='q30')
    ticket_array.add_ticket(ticket_code='BOUNT00', ticket_price=5, ticket_service_fee=1)
    ticket_array.add_ticket(ticket_code='BOUNT00', ticket_price=5, ticket_service_fee=1)
    ticket_array.add_ticket(ticket_code='BOUNT00', ticket_price=5, ticket_service_fee=1)

    assert ticket_array.total_ticket_fees() == 3


def test_array_to_dict():
    ticket_array = VIFTicketArray(record_code='q30')
    ticket_array.add_ticket(ticket_code='BOUNT00', ticket_price=5, ticket_service_fee=1)
    expected = {
        100101: 'BOUNT00',
        100102: 5,
        100103: 1
    }
    assert ticket_array.data() == expected


def test_array_to_dict_zero_price():
    ticket_array = VIFTicketArray(record_code='q30')
    ticket_array.add_ticket(ticket_code='BOUNT00', ticket_price=0, ticket_service_fee=1)
    expected = {
        100101: 'BOUNT00',
        100102: 0,
        100103: 1,
    }
    assert ticket_array.data() == expected


def test_array_to_dict_multiple_tickets():
    ticket_array = VIFTicketArray(record_code='q30')
    ticket_array.add_ticket(ticket_code='BOUNT00', ticket_price=5, ticket_service_fee=1)
    ticket_array.add_ticket(ticket_code='BOUNT00', ticket_price=5, ticket_service_fee=1)
    ticket_array.add_ticket(ticket_code='BOUNT00', ticket_price=5, ticket_service_fee=1)
    expected = {
        100101: 'BOUNT00',
        100102: 5,
        100103: 1,
        100201: 'BOUNT00',
        100202: 5,
        100203: 1,
        100301: 'BOUNT00',
        100302: 5,
        100303: 1
    }
    assert ticket_array.data() == expected


def test_array_maps_p30_keys():
    ticket_array = VIFTicketArray(record_code='p30')
    ticket_array.add_ticket(ticket_code='BOUNT00', ticket_price=5, ticket_service_fee=1)
    ticket_array.add_ticket(ticket_code='BOUNT00', ticket_price=5, ticket_service_fee=1)
    ticket_array.add_ticket(ticket_code='BOUNT00', ticket_price=5, ticket_service_fee=1)
    expected = {
        100101: 'BOUNT00',
        100103: 5,
        100108: 1,
        100201: 'BOUNT00',
        100203: 5,
        100208: 1,
        100301: 'BOUNT00',
        100303: 5,
        100308: 1
    }
    assert ticket_array.data() == expected


def test_parse_friendly_data_into_ticket_array():
    named_data = [
        {
            'ticket_code': 'BOUNT00',
            'ticket_price': 10.0,
            'seat_name': 'A 12',
            'ticket_service_fee': 1.0
        },
        {
            'ticket_code': 'BOUNT00',
            'ticket_price': 10.0,
            'seat_name': 'A 11',
            'ticket_service_fee': 1.0
        }
    ]
    ticket_array = VIFTicketArray(record_code='q30', named_data=named_data)
    assert ticket_array.count() == 2
    assert ticket_array.data() == {
        100101: 'BOUNT00',
        100102: 10.0,
        100103: 1.0,
        100104: 'A 12',
        100201: 'BOUNT00',
        100202: 10.0,
        100203: 1.0,
        100204: 'A 11'
    }
