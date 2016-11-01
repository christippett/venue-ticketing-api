import pytest

from venue import VIFTicketArray


def test_count_ticket_array():
    ticket_array = VIFTicketArray()
    ticket_array.add_ticket(ticket_code='BOUNT00', price=5, service_fee=1)
    ticket_array.add_ticket(ticket_code='BOUNT00', price=5, service_fee=1)
    ticket_array.add_ticket(ticket_code='BOUNT00', price=5, service_fee=1)

    assert ticket_array.count() == 3


def test_sum_ticket_prices():
    ticket_array = VIFTicketArray()
    ticket_array.add_ticket(ticket_code='BOUNT00', price=5, service_fee=1)
    ticket_array.add_ticket(ticket_code='BOUNT00', price=5, service_fee=1)
    ticket_array.add_ticket(ticket_code='BOUNT00', price=5, service_fee=1)

    assert ticket_array.total_ticket_prices() == 15


def test_sum_ticket_fees():
    ticket_array = VIFTicketArray()
    ticket_array.add_ticket(ticket_code='BOUNT00', price=5, service_fee=1)
    ticket_array.add_ticket(ticket_code='BOUNT00', price=5, service_fee=1)
    ticket_array.add_ticket(ticket_code='BOUNT00', price=5, service_fee=1)

    assert ticket_array.total_ticket_fees() == 3


def test_array_to_dict():
    ticket_array = VIFTicketArray()
    ticket_array.add_ticket(ticket_code='BOUNT00', price=5, service_fee=1)
    d = ticket_array.dict()
    expected = {
        '100101': 'BOUNT00',
        '100102': 5,
        '100103': 1
    }
    assert d == expected


def test_array_to_dict_zero_price():
    ticket_array = VIFTicketArray()
    ticket_array.add_ticket(ticket_code='BOUNT00', price=0, service_fee=1)
    d = ticket_array.dict()
    expected = {
        '100101': 'BOUNT00',
        '100103': 1
    }
    assert d == expected


def test_array_to_dict_multiple_tickets():
    ticket_array = VIFTicketArray()
    ticket_array.add_ticket(ticket_code='BOUNT00', price=5, service_fee=1)
    ticket_array.add_ticket(ticket_code='BOUNT00', price=5, service_fee=1)
    ticket_array.add_ticket(ticket_code='BOUNT00', price=5, service_fee=1)
    d = ticket_array.dict()
    expected = {
        '100101': 'BOUNT00',
        '100102': 5,
        '100103': 1,
        '100201': 'BOUNT00',
        '100202': 5,
        '100203': 1,
        '100301': 'BOUNT00',
        '100302': 5,
        '100303': 1
    }
    assert d == expected
