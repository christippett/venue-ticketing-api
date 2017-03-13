import pytest

from venue.vif_ticket_array import VIFPaymentArray
from venue.vif_record import VIFRecord


def test_count_payment_array():
    payment_array = VIFPaymentArray(record_code='q31')
    payment_array.add_payment(payment_category=14, payment_provider='Stripe', amount_paid=10.0)
    payment_array.add_payment(payment_category=14, payment_provider='Stripe', amount_paid=10.0)
    payment_array.add_payment(payment_category=14, payment_provider='Stripe', amount_paid=10.0)
    assert payment_array.count() == 3


def test_array_to_dict():
    payment_array = VIFPaymentArray(record_code='q31')
    payment_array.add_payment(payment_category=14, payment_provider='Stripe', amount_paid=10.0)
    expected = {
        1101: 14,
        1102: 'Stripe',
        1103: 10.0
    }
    assert payment_array.data() == expected


def test_array_to_dict_multiple_tickets():
    payment_array = VIFPaymentArray(record_code='q31')
    payment_array.add_payment(payment_category=14, payment_provider='Stripe', amount_paid=10.0)
    payment_array.add_payment(payment_category=14, payment_provider='Stripe', amount_paid=10.0)
    payment_array.add_payment(payment_category=14, payment_provider='Stripe', amount_paid=10.0)
    expected = {
        1101: 14,
        1102: 'Stripe',
        1103: 10.0,
        1201: 14,
        1202: 'Stripe',
        1203: 10.0,
        1301: 14,
        1302: 'Stripe',
        1303: 10.0
    }
    assert payment_array.data() == expected


def test_can_convert_payment_array_from_text_1():
    commit_request_content = ('{q31}{2}1769{4}44.80{5}42424XXXXXXX4242{7}0419925750{11}WWW{1001}1'
                              '{1101}4{1102}NAB{1103}44.80{1104}42424XXXXXXX4242{1105}'
                              '{1106}Test at 2017-01-10 20:01:00 by Ticketbounty{1107}VISA'
                              '{1108}{1109}47R839373V998061D{1111}1')
    commit_record = VIFRecord(raw_content=commit_request_content)
    payment_array = commit_record.payment_array()
    assert payment_array.count() == 1
