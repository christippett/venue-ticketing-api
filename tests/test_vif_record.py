import re

import pytest

from venue.vif_record import VIFRecord


def test_raw_content_converts_to_data():
    raw_content = '{vrq}{1}BARKER{2}ABCD{3}1{4}Test{8}108193016648'
    message = VIFRecord(raw_content=raw_content)
    assert message.data == {
        1: 'BARKER',
        2: 'ABCD',
        3: '1',
        4: 'Test',
        8: '108193016648'
    }


def test_extract_record_code_from_raw_content():
    raw_content = '{vrq}{1}BARKER{2}ABCD{3}1{4}Test{8}108193016648'
    message = VIFRecord(raw_content=raw_content)
    assert message.record_code == 'vrq'


def test_named_data_fields_convert_to_integer_keys():
    data = {
        'site_name': 'BARKER',
        'packet_id': 'ABCD',
        'request_code': 1,
        'comment': 'Test',
        'auth_info': '108193016648'
    }
    message = VIFRecord(record_code='vrq', data=data)
    assert message.data == {
        1: 'BARKER',
        2: 'ABCD',
        3: 1,
        4: 'Test',
        8: '108193016648'
    }


def test_data_fields_not_parsed_if_keys_already_integers():
    data = {
        1: 'BARKER',
        2: 'ABCD',
        3: '1',
        4: 'Test',
        8: '108193016648'
    }
    message = VIFRecord(data=data)
    assert message.data == {
        1: 'BARKER',
        2: 'ABCD',
        3: '1',
        4: 'Test',
        8: '108193016648'
    }


def test_formatted_content_1():
    data = {
        'site_name': 'BARKER',
        'packet_id': 'ABCD',
        'request_code': '1',
        'comment': 'Test',
        'auth_info': '108193016648'
    }
    message = VIFRecord(record_code='vrq', data=data)
    assert message.content() == '{vrq}{1}BARKER{2}ABCD{3}1{4}Test{8}108193016648'


def test_formatted_content_2():
    raw_content = '{vrq}{1}BARKER{2}ABCD{3}1{4}Test{8}108193016648'
    message = VIFRecord(raw_content=raw_content)
    assert raw_content == message.content()


def test_formatted_content_includes_record_code_when_available():
    data = {
        1: 'BARKER',
        2: 'ABCD',
        3: '1',
        4: 'Test',
        8: '108193016648'
    }
    message = VIFRecord(record_code='vrq', data=data)
    assert message.content() == '{vrq}{1}BARKER{2}ABCD{3}1{4}Test{8}108193016648'


def test_formatted_content_excludes_record_code_when_not_available_1():
    data = {
        1: 'BARKER',
        2: 'ABCD',
        3: '1',
        4: 'Test',
        8: '108193016648'
    }
    message = VIFRecord(data=data)
    assert message.content() == '{1}BARKER{2}ABCD{3}1{4}Test{8}108193016648'


def test_formatted_content_excludes_record_code_when_not_available_2():
    raw_content = '{1}BARKER{2}ABCD{3}1{4}Test{8}108193016648'
    message = VIFRecord(raw_content=raw_content)
    assert message.content() == '{1}BARKER{2}ABCD{3}1{4}Test{8}108193016648'


def test_unable_to_format_content_if_record_code_not_provided():
    data = {
        'site_name': 'BARKER',
        'packet_id': 'ABCD',
        'request_code': 1,
        'comment': 'Test',
        'auth_info': '108193016648'
    }
    with pytest.raises(Exception):
        VIFRecord(data=data)


def test_mapping_of_data_to_field_names_1():
    data = {
        'site_name': 'BARKER',
        'packet_id': 'ABCD',
        'request_code': 1,
        'comment': 'Test',
        'auth_info': '108193016648'
    }
    message = VIFRecord(record_code='vrq', data=data)
    assert message.friendly_format() == data


def test_mapping_of_data_to_field_names_2():
    data = {
        1: 'BARKER',
        2: 'ABCD',
        3: 1,
        4: 'Test',
        8: '108193016648'
    }
    message = VIFRecord(record_code='vrq', data=data)
    assert message.friendly_format() == {
        'site_name': 'BARKER',
        'packet_id': 'ABCD',
        'request_code': 1,
        'comment': 'Test',
        'auth_info': '108193016648'
    }


def test_mapping_of_data_to_field_names_3():
    raw_content = '{vrq}{1}BARKER{2}ABCD{3}1{4}Test{8}108193016648'
    message = VIFRecord(raw_content=raw_content)
    assert message.friendly_format() == {
        'site_name': 'BARKER',
        'packet_id': 'ABCD',
        'request_code': 1,
        'comment': 'Test',
        'auth_info': '108193016648'
    }


def test_mapping_of_data_to_field_names_including_tickets_2():
    data = {
        1: 123,             # workstation id
        2: 'TKTBTY',          # user code
        3: 999,             # session number
        4: 1,                 # transaction type
        5: 'CUSTNO123',       # customer reference
        10: 15.0,             # total ticket prices
        11: 3.0,              # total ticket fees
        13: 18.0,             # total transaction price
        100001: 3,            # elements in ticket array
        100101: 'BOUNT00',    # ticket code (1)
        100102: 5,            # ticket price (1)
        100103: 1,            # ticket service fee (1)
        100201: 'BOUNT00',    # ticket code (2)
        100202: 5,            # ticket price (2)
        100203: 1,            # ticket service fee (3)
        100301: 'BOUNT00',    # ticket code (3)
        100302: 5,            # ticket price (2)
        100303: 1             # ticket service fee (3)
    }
    message = VIFRecord(record_code='q30', data=data)
    assert message.friendly_format() == {
        'workstation_id': 123,
        'usercode': 'TKTBTY',
        'session_number': 999,
        'transaction_type': 1,
        'customer_reference': 'CUSTNO123',
        'total_ticket_price': 15.0,
        'total_ticket_fees': 3.0,
        'total_transaction_price': 18.0,
        'ticket_count': 3,
        'tickets': [
            {
                'ticket_code': 'BOUNT00',
                'ticket_price': 5.0,
                'ticket_service_fee': 1.0
            },
            {
                'ticket_code': 'BOUNT00',
                'ticket_price': 5.0,
                'ticket_service_fee': 1.0
            },
            {
                'ticket_code': 'BOUNT00',
                'ticket_price': 5.0,
                'ticket_service_fee': 1.0
            }
        ]
    }


def test_mapping_of_data_to_field_names_including_tickets_3():
    raw_content = ('{q30}{1}123{2}TKTBTY{3}999{4}1{5}CUSTNO123'
                   '{10}15.0{11}3.0{13}18.0{100001}3'
                   '{100101}BOUNT00{100102}5{100103}1'
                   '{100201}BOUNT00{100202}5{100203}1'
                   '{100301}BOUNT00{100302}5{100303}1')
    message = VIFRecord(raw_content=raw_content)
    assert message.friendly_format() == {
        'workstation_id': 123,
        'usercode': 'TKTBTY',
        'session_number': 999,
        'transaction_type': 1,
        'customer_reference': 'CUSTNO123',
        'total_ticket_price': 15.0,
        'total_ticket_fees': 3.0,
        'total_transaction_price': 18.0,
        'ticket_count': 3,
        'tickets': [
            {
                'ticket_code': 'BOUNT00',
                'ticket_price': 5.0,
                'ticket_service_fee': 1.0
            },
            {
                'ticket_code': 'BOUNT00',
                'ticket_price': 5.0,
                'ticket_service_fee': 1.0
            },
            {
                'ticket_code': 'BOUNT00',
                'ticket_price': 5.0,
                'ticket_service_fee': 1.0
            }
        ]
    }
