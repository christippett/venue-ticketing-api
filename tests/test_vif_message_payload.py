import pytest

from venue.vif_message_payload import VIFMessagePayload
from venue.vif_record import VIFRecord


def test_header_extracted_from_content():
    content = ('{vrp}{1}BARKER{2}6000!;'
               '\n;' + r'Ticketing VIF file, generated at 9:53;35.552pm by E:\Ven\bin\VIFGateway.exe'
               '\n;'
               '\n;'
               '\n; Header'
               '\n;'
               '\n' + r'{hdr}{1}E:\Ven\bin\VIFGateway.exe{2}20170311215335{4}2'
               '\n;'
               '\n; Installation details'
               '\n;'
               '\n{ins}{2}Mt Barker Cinemas!{3}Wallis{4}BARKER{5}6{6}606{7}Australia'
               '{8}Mt Barker Cinemas{9}6{10}6{11}05{12}20150625095222{13}WALLIS'
               '{14}84 764 357 070{15}SA{16}1{41}2{42}10{43}10{51} {52} {55}20160513000000'
               '{56}20160513000000{57}19970912050000{58}19970912235959'
               '\n;'
               '\n; Distributors'
               '\n;'
               '\n{dis}{1}1{2}Filmways{3}0{17}11'
               '\n{dis}{1}2{2}Fourth Wall{3}4WALL{17}11'
               '\n{dis}{1}3{2}A Tiny House Documentary{3}A TINY{17}11'
               '\n{dis}{1}19{2}Binding Films{3}BINDING{17}11')
    message_payload = VIFMessagePayload(content=content)
    assert message_payload.header_content == '{vrp}{1}BARKER{2}6000'


def test_header_converts_to_vif_record():
    content = ('{vrp}{1}BARKER{2}6000!;'
               '\n;' + r'Ticketing VIF file, generated at 9:53;35.552pm by E:\Ven\bin\VIFGateway.exe'
               '\n;'
               '\n;'
               '\n; Header'
               '\n;'
               '\n' + r'{hdr}{1}E:\Ven\bin\VIFGateway.exe{2}20170311215335{4}2'
               '\n;'
               '\n; Installation details'
               '\n;'
               '\n{ins}{2}Mt Barker Cinemas!{3}Wallis{4}BARKER{5}6{6}606{7}Australia'
               '{8}Mt Barker Cinemas{9}6{10}6{11}05{12}20150625095222{13}WALLIS'
               '{14}84 764 357 070{15}SA{16}1{41}2{42}10{43}10{51} {52} {55}20160513000000'
               '{56}20160513000000{57}19970912050000{58}19970912235959'
               '\n;'
               '\n; Distributors'
               '\n;'
               '\n{dis}{1}1{2}Filmways{3}0{17}11'
               '\n{dis}{1}2{2}Fourth Wall{3}4WALL{17}11'
               '\n{dis}{1}3{2}A Tiny House Documentary{3}A TINY{17}11'
               '\n{dis}{1}19{2}Binding Films{3}BINDING{17}11')
    message_payload = VIFMessagePayload(content=content)
    header = message_payload.header

    assert isinstance(header, VIFRecord)
    assert header.content() == '{vrp}{1}BARKER{2}6000'
    assert header.data() == {
        1: 'BARKER',
        2: '6000'
    }
    assert header.friendly_data() == {
        'site_name': 'BARKER',
        'packet_id': '6000'
    }


def test_body_returns_multiple_vif_records():
    content = ('{vrp}{1}BARKER{2}6000!;'
               '\n;' + r'Ticketing VIF file, generated at 9:53;35.552pm by E:\Ven\bin\VIFGateway.exe'
               '\n;'
               '\n;'
               '\n; Header'
               '\n;'
               '\n' + r'{hdr}{1}E:\Ven\bin\VIFGateway.exe{2}20170311215335{4}2'
               '\n;'
               '\n; Installation details'
               '\n;'
               '\n{ins}{2}Mt Barker Cinemas!{3}Wallis{4}BARKER{5}6{6}606{7}Australia'
               '{8}Mt Barker Cinemas{9}6{10}6{11}05{12}20150625095222{13}WALLIS'
               '{14}84 764 357 070{15}SA{16}1{41}2{42}10{43}10{51} {52} {55}20160513000000'
               '{56}20160513000000{57}19970912050000{58}19970912235959'
               '\n;'
               '\n; Distributors'
               '\n;'
               '\n{dis}{1}1{2}Filmways{3}0{17}11'
               '\n{dis}{1}2{2}Fourth Wall{3}4WALL{17}11'
               '\n{dis}{1}3{2}A Tiny House Documentary{3}A TINY{17}11'
               '\n{dis}{1}19{2}Binding Films{3}BINDING{17}11')
    message_payload = VIFMessagePayload(content=content)
    body = message_payload.body
    assert len(body) == 6
    assert isinstance(body[0], VIFRecord)
    assert body[0].content() == r'{hdr}{1}E:\Ven\bin\VIFGateway.exe{2}20170311215335{4}2'
    assert body[0].data() == {
        1: r'E:\Ven\bin\VIFGateway.exe',
        2: '20170311215335',
        4: 2
    }
    assert body[0].friendly_data() == {
        'exporting_program': r'E:\Ven\bin\VIFGateway.exe',
        'export_datetime': '20170311215335',
        'vif_detail': 2
    }


def test_parsed_content_back_to_text():
    content = ('{vrp}{1}BARKER{2}6000!;'
               '\n;' + r'Ticketing VIF file, generated at 9:53;35.552pm by E:\Ven\bin\VIFGateway.exe'
               '\n;'
               '\n;'
               '\n; Header'
               '\n;'
               '\n' + r'{hdr}{1}E:\Ven\bin\VIFGateway.exe{2}20170311215335{4}2'
               '\n;'
               '\n; Installation details'
               '\n;'
               '\n{ins}{2}Mt Barker Cinemas!{3}Wallis{4}BARKER{5}6{6}606{7}Australia'
               '{8}Mt Barker Cinemas{9}6{10}6{11}05{12}20150625095222{13}WALLIS'
               '{14}84 764 357 070{15}SA{16}1{41}2{42}10{43}10{51} {52} {55}20160513000000'
               '{56}20160513000000{57}19970912050000{58}19970912235959'
               '\n;'
               '\n; Distributors'
               '\n;'
               '\n{dis}{1}1{2}Filmways{3}0{17}11'
               '\n{dis}{1}2{2}Fourth Wall{3}4WALL{17}11'
               '\n{dis}{1}3{2}A Tiny House Documentary{3}A TINY{17}11'
               '\n{dis}{1}19{2}Binding Films{3}BINDING{17}11')
    message_payload = VIFMessagePayload(content=content)
    parsed_content = message_payload.content()
    assert parsed_content == (
        '{vrp}{1}BARKER{2}6000!'  # no newline after header
        r'{hdr}{1}E:\Ven\bin\VIFGateway.exe{2}20170311215335{4}2'
        '\n{ins}{2}Mt Barker Cinemas!{3}Wallis{4}BARKER{5}6{6}606{7}Australia'
        '{8}Mt Barker Cinemas{9}6{10}6{11}05{12}20150625095222{13}WALLIS'
        '{14}84 764 357 070{15}SA{16}1{41}2{42}10{43}10{51} {52} {55}20160513000000'
        '{56}20160513000000{57}19970912050000{58}19970912235959'
        '\n{dis}{1}1{2}Filmways{3}0{17}11'
        '\n{dis}{1}2{2}Fourth Wall{3}4WALL{17}11'
        '\n{dis}{1}3{2}A Tiny House Documentary{3}A TINY{17}11'
        '\n{dis}{1}19{2}Binding Films{3}BINDING{17}11')


def test_parsing_when_header_and_body_on_one_line():
    content = ('{vrp}{1}NRLNGA{2}8edi!'
               '{p30}{3}Cinema 03{4}Cinema Three{5}ROGUEONE{6}Rogue One: A Star Wars St'
               '{7}20170111104500{9}4.8{10}44.8'
               '{1001}A 13{1002}A 12{1003}A 11{1004}A 10{100001}4'
               '{100101}BOUNT00{100103}10{100105}A 13{100106}Tkt Bounty Web{100108}1.2'
               '{100201}BOUNT00{100203}10{100205}A 12{100206}Tkt Bounty Web{100208}1.2'
               '{100301}BOUNT00{100303}10{100305}A 11{100306}Tkt Bounty Web{100308}1.2'
               '{100401}BOUNT00{100403}10{100405}A 10{100406}Tkt Bounty Web{100408}1.2')
    message_payload = VIFMessagePayload(content=content)
    assert content == message_payload.content()
    assert message_payload.header.record_code == 'vrp'
    assert len(message_payload.body) == 1
    assert message_payload.body[0].record_code == 'p30'


def test_parsing_when_body_record_code_unavailable():
    content = ('{vrp}{1}NRLNGA{2}8edi!'
               '{3}Cinema 03{4}Cinema Three{5}ROGUEONE{6}Rogue One: A Star Wars St'
               '{7}20170111104500{9}4.8{10}44.8'
               '{1001}A 13{1002}A 12{1003}A 11{1004}A 10{100001}4'
               '{100101}BOUNT00{100103}10{100105}A 13{100106}Tkt Bounty Web{100108}1.2'
               '{100201}BOUNT00{100203}10{100205}A 12{100206}Tkt Bounty Web{100208}1.2'
               '{100301}BOUNT00{100303}10{100305}A 11{100306}Tkt Bounty Web{100308}1.2'
               '{100401}BOUNT00{100403}10{100405}A 10{100406}Tkt Bounty Web{100408}1.2')
    message_payload = VIFMessagePayload(content=content)
    assert content == message_payload.content()
    assert message_payload.header.record_code == 'vrp'
    assert len(message_payload.body) == 1
