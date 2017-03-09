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
        'request_code': '1',
        'comment': 'Test',
        'auth_info': '108193016648'
    }
    message = VIFRecord(record_code='vrq', data=data)
    assert message.data == {
        1: 'BARKER',
        2: 'ABCD',
        3: '1',
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
        'request_code': '1',
        'comment': 'Test',
        'auth_info': '108193016648'
    }
    with pytest.raises(Exception):
        VIFRecord(data=data)


def test_mapping_of_data_to_field_names_1():
    data = {
        'site_name': 'BARKER',
        'packet_id': 'ABCD',
        'request_code': '1',
        'comment': 'Test',
        'auth_info': '108193016648'
    }
    message = VIFRecord(record_code='vrq', data=data)
    assert message.format_data() == data


def test_mapping_of_data_to_field_names_2():
    data = {
        1: 'BARKER',
        2: 'ABCD',
        3: '1',
        4: 'Test',
        8: '108193016648'
    }
    message = VIFRecord(record_code='vrq', data=data)
    assert message.format_data() == {
        'site_name': 'BARKER',
        'packet_id': 'ABCD',
        'request_code': '1',
        'comment': 'Test',
        'auth_info': '108193016648'
    }


def test_mapping_of_data_to_field_names_3():
    raw_content = '{vrq}{1}BARKER{2}ABCD{3}1{4}Test{8}108193016648'
    message = VIFRecord(raw_content=raw_content)
    assert message.format_data() == {
        'site_name': 'BARKER',
        'packet_id': 'ABCD',
        'request_code': '1',
        'comment': 'Test',
        'auth_info': '108193016648'
    }
