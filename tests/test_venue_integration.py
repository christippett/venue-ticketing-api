import re

import pytest

from venue import VIFMessage, VIFGateway


def test_unwrap_dict():
    dict_data = {
        '1': 'value1',
        '2': 'value2',
        '3': 'value3'
    }
    assert VIFMessage.format_vif_message(None, dict_data) == "{1}value1{2}value2{3}value3"


def test_unwrap_dict_in_order():
    dict_data = {
        '3': 'value3',
        '1': 'value1',
        '2': 'value2'
    }
    assert VIFMessage.format_vif_message(None, dict_data) == "{1}value1{2}value2{3}value3"


def test_header_keys_should_be_numeric():
    message = VIFMessage(record_code='vrq', site_name='BARKER',
                         packet_id='ABCD', request_code=1, comment='Test',
                         auth_info='108193016648')
    header = message.header_dict()
    assert isinstance(header, dict)
    for key, value in header.items():
        int(key)


def test_vif_format_header():
    message = VIFMessage(record_code='vrq', site_name='BARKER',
                         packet_id='ABCD', request_code=1, comment='Test',
                         auth_info='108193016648')
    expected = '{vrq}{1}BARKER{2}ABCD{3}1{4}Test{8}108193016648'
    assert expected == message.header()


def test_vif_message_dict():
    message = VIFMessage(record_code='vrq', site_name='BARKER',
                         packet_id='ABCD', request_code=1, comment='Test',
                         auth_info='108193016648')
    message_dict = message.header_dict(get_field_names=True)
    assert message_dict['site_name'] == 'BARKER'
    assert message_dict['packet_id'] == 'ABCD'
    assert message_dict['request_code'] == 1
    assert message_dict['comment'] == 'Test'
    assert message_dict['auth_info'] == '108193016648'


def test_no_comment_if_none_entered():
    message = VIFMessage(record_code='vrq', site_name='BARKER',
                         packet_id='ABCD', request_code=1,
                         auth_info='108193016648')
    message_dict = message.header_dict(get_field_names=True)
    assert message_dict.get('comment', '') == ''
    comment_pattern = re.compile(r'(\{4\}.*)', re.IGNORECASE)
    assert not comment_pattern.match(message.content)


def test_vif_handshake_message():
    gateway = VIFGateway(site_name='BARKER', host='127.0.0.1',
                         auth_key='1081930166', agent_no='48')
    message = gateway.create_message(request_code=1)
    header = message.header_dict(get_field_names=True)

    assert isinstance(message, VIFMessage)
    assert header['request_code'] == 1
    assert message.header() + chr(3) == message.content


def test_raise_connection_error_if_unable_to_connect():
    gateway = VIFGateway(site_name='BARKER', host='127.0.0.1',
                         auth_key='1081930166', agent_no='48')
    with pytest.raises(ConnectionError):
        gateway.handshake()


def test_vif_format_message():
    dict_data = {
        '3': 'test3',
        '1': 'test1',
        '2': 'test2',
    }
    message = VIFMessage(record_code='vrq', site_name='BARKER',
                         packet_id='ABCD', request_code=1, comment='Test',
                         auth_info='108193016648', body=dict_data)
    expected = '{vrq}{1}BARKER{2}ABCD{3}1{4}Test{8}108193016648' \
               '!{1}test1{2}test2{3}test3' + chr(3)
    assert expected == message.content


def test_vif_parse_response():
    content = '{vrq}{1}BARKER{2}ABCD{3}1{4}Test{8}108193016648' \
              '!{1}test1{2}test2{3}test3' + chr(3)
    message = VIFMessage(content=content)
    assert content == message.content


def test_vif_parse_response_header():
    content = '{vrq}{1}BARKER{2}ABCD{3}1{4}Test{8}108193016648' \
              '!{1}test1{2}test2{3}test3' + chr(3)
    message = VIFMessage(content=content)
    header = message.header_dict()
    assert header.get('1') == 'BARKER'
    assert header.get('2') == 'ABCD'
    assert header.get('3') == '1'
    assert header.get('4') == 'Test'
    assert header.get('8') == '108193016648'


def test_vif_parse_response_body():
    content = '{vrq}{1}BARKER{2}ABCD{3}1{4}Test{8}108193016648' \
              '!{1}test1{2}test2{3}test3' + chr(3)
    message = VIFMessage(content=content)
    body = message.body_dict()
    assert body.get('1') == 'test1'
    assert body.get('2') == 'test2'
    assert body.get('3') == 'test3'


def test_vif_parse_response_no_body():
    content = '{vrq}{1}BARKER{2}ABCD{3}1{4}Test{8}108193016648' + chr(3)
    message = VIFMessage(content=content)
    assert content == message.content


def test_vif_parse_response_no_body_with_exclamation():
    content = '{mov}{1}BARKER{2}ABCD{3}1{4}Test!{8}108193016648' + chr(3)
    message = VIFMessage(content=content)
    header = message.header_dict()
    assert content == message.content
    assert header.get('4') == 'Test!'
    assert header.get('8') == '108193016648'


def test_vif_parse_response_contains_body_and_exclamation():
    content = '{vrq}{1}BARKER{2}ABCD{3}1{4}EXCLAMAT!ON{5}Test5' \
              '!{1}test1{2}test2{3}test3' + chr(3)
    message = VIFMessage(content=content)
    header = message.header_dict()
    body = message.body_dict()
    assert header.get('4') == 'EXCLAMAT!ON'
    assert header.get('5') == 'Test5'
    assert body.get('1') == 'test1'
