import pytest

from venue.vif_record import VIFRecord
from venue.vif_message import VIFMessage
from venue.vif_gateway import VIFGateway
from venue.vif_ticket_array import VIFTicketArray


def test_vif_init_transaction_request():
    # Add 3 tickets to array
    ticket_array = VIFTicketArray(record_code='q30')
    ticket_array.add_ticket(ticket_code='BOUNT00', ticket_price=5, ticket_service_fee=1)
    ticket_array.add_ticket(ticket_code='BOUNT00', ticket_price=5, ticket_service_fee=1)
    ticket_array.add_ticket(ticket_code='BOUNT00', ticket_price=5, ticket_service_fee=1)

    record_data = {
        'workstation_id': 123,
        'user_code': 'TKTBTY',
        'session_number': 999,
        'transaction_type': 1,
        'customer_reference': 'CUSTNO123',
        'total_ticket_prices': 15.0,
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
    q30_record = VIFRecord(record_code='q30', data=record_data)
    expected = {
        1: 123,               # workstation id
        2: 'TKTBTY',          # user code
        3: 999,               # session number
        4: 1,                 # transaction type
        5: 'CUSTNO123',       # customer reference
        10: 15.0,             # total ticket prices
        11: 3.0,              # total ticket fees
        13: 18.0,             # total transaction price
        100001: 3,            # elements in ticket array
        100101: 'BOUNT00',    # ticket code (1)
        100102: 5.0,          # ticket price (1)
        100103: 1.0,          # ticket service fee (1)
        100201: 'BOUNT00',    # ticket code (2)
        100202: 5.0,          # ticket price (2)
        100203: 1.0,          # ticket service fee (3)
        100301: 'BOUNT00',    # ticket code (3)
        100302: 5.0,          # ticket price (2)
        100303: 1.0           # ticket service fee (3)
    }
    assert expected == q30_record.data()


def test_vif_init_transaction_response():
    response_content = ('{p30}{3}Cinema 02{4}Cinema Two{5}MOANA{6}Moana{7}20170110100000{8}15{9}2{10}37'
                        '{1001}A 12{1002}A 11{100001}2'
                        '{100101}BOUNT00{100103}10{100105}A 12{100106}Tkt Bounty Web{100108}1'
                        '{100201}BOUNT00{100203}10{100205}A 11{100206}Tkt Bounty Web{100208}1')
    p30_record = VIFRecord(raw_content=response_content)
    expected = {
        3: 'Cinema 02',
        4: 'Cinema Two',
        5: 'MOANA',
        6: 'Moana',
        7: '20170110100000',
        8: 15.0,
        9: 2.0,
        10: 37.0,
        1001: 'A 12',
        1002: 'A 11',
        100001: 2,
        100101: 'BOUNT00',
        100103: 10.0,
        100105: 'A 12',
        100106: 'Tkt Bounty Web',
        100108: 1.0,
        100201: 'BOUNT00',
        100203: 10.0,
        100205: 'A 11',
        100206: 'Tkt Bounty Web',
        100208: 1.0,
    }
    assert expected == p30_record.data()


@pytest.mark.skip(reason="WIP")
def test_vif_init_transaction_response_2(monkeypatch):
    def mocksend(self, message):
        response_content = (b'{vrp}{1}BARKER{2}6A86!'
                            b'{p30}{3}Cinema 02{4}Cinema Two{5}MOANA{6}Moana{7}20170110100000{8}15{9}2{10}37'
                            b'{1001}A 12{1002}A 11{100001}2'
                            b'{100101}BOUNT00{100103}10{100105}A 12{100106}Tkt Bounty Web{100108}1'
                            b'{100201}BOUNT00{100203}10{100205}A 11{100206}Tkt Bounty Web{100208}1')
        return self.parse_response([response_content])
    monkeypatch.setattr(VIFGateway, 'send', mocksend)

    # Construct init_transaction message
    request_content = ('{vrq}{1}BARKER{2}6A86{3}30{4}VIFGateway Test{5}3{8}108193016648!'
                       '{1}627{2}VifTest{3}132417{4}1{11}2{12}15{13}37{100001}2'
                       '{100101}BOUNT00{100102}10{100103}1'
                       '{100201}BOUNT00{100202}10{100203}1{10}20')
    request_message = VIFMessage(content=request_content)

    # Send message
    gateway = VIFGateway(site_name='BARKER', host='127.0.0.1',
                         auth_key='1081930166', agent_no='48')
    response = gateway.send(request_message)

    # Assert monkeypatched 'send' function returns appropriately formatted response
    assert 'vrp' in response
    assert len(response['vrp']) == 1
    assert 'header' in response['vrp'][0]
    assert 'body' in response['vrp'][0]

    # Assert response


@pytest.mark.skip(reason="WIP")
def test_vif_init_transaction_seat_taken():
    request_content = ('{vrq}{1}BARKER{2}AFF5{3}30{4}VIFGateway Test{5}3{8}108193016648!'
                       '{1}627{2}VifTest{3}132417{4}1{13}10{100001}1'
                       '{100101}BOUNT00{100102}10{100104}A12{10}10')

    response_content = '{vrp}{1}BARKER{2}AFF5{3}70415{5}Seat is already locked!'


@pytest.mark.skip(reason="WIP")
def test_vif_get_available_seats():
    request_content = ('{vrq}{1}BARKER{2}AFF6{3}20{4}VIFGateway Test{5}3{8}108193016648!'
                       '{1}132417{2}1')

    response_content = ('{vrp}{1}BARKER{2}AFF6!'
                        '{pl4}{1}N 22{2}N 21{3}N 20{4}N 19{5}N 18{6}N 17{7}N 16{8}N 15{9}N 14{10}N 13'
                        '{11}N 12{12}N 11{13}N 10{14}N 9{15}N 8{16}N 7{17}N 6{18}N 5{19}N 4{20}N 3'
                        '{21}N 2{22}N 1{23}M 22{24}M 21{25}M 20{26}M 19{27}M 18{28}M 17{29}M 16{30}M 15'
                        '{31}M 14{32}M 13{33}M 12{34}M 11{35}M 10{36}M 9{37}M 8{38}M 7{39}M 6{40}M 5'
                        '{41}M 4{42}M 3{43}M 2{44}M 1{45}L 22{46}L 21{47}L 20{48}L 19{49}L 18{50}L 17'
                        '{51}L 16{52}L 15{53}L 14{54}L 13{55}L 12{56}L 11{57}L 10{58}L 9{59}L 8{60}L 7'
                        '{61}L 6{62}L 5{63}L 4{64}L 3{65}L 2{66}L 1{67}K 22{68}K 21{69}K 20{70}K 19'
                        '{71}K 18{72}K 17{73}K 16{74}K 15{75}K 14{76}K 13{77}K 12{78}K 11{79}K 10{80}K 9'
                        '{81}K 8{82}K 7{83}K 6{84}K 5{85}K 4{86}K 3{87}K 2{88}K 1{89}J 22{90}J 21'
                        '{91}J 20{92}J 19{93}J 18{94}J 17{95}J 16{96}J 15{97}J 14{98}J 13{99}J 12{100}J 11')


@pytest.mark.skip(reason="WIP")
def test_vif_commit_credit_card_transaction():
    request_content = ('{vrq}{1}BARKER{2}B003{3}31{4}VIFGateway Test{5}3{8}108193016648!'
                       '{2}627{3}ExternalReference{4}10{1001}1'
                       '{1101}4{1102}Test Provider{1103}10{1104}4242424242424242{1105}123{1106}John Citizen{1107}VISA{1108}0518{1109}BankTxn-0123456789{1110}592{1111}1')

    response_content = ('{vrp}{1}BARKER{2}B003!'
                        '{p31}{1}15545{2}1777013{3}4242424242424242{4}1554551020'
                        '{1001}D 17{100001}1'
                        '{100101}BOUNT00{100103}10{100105}D 17{100106}Tkt Bounty Web{100107}2656938{100110}Z0R6QCXLTMVMYP')


@pytest.mark.skip(reason="WIP")
def test_vif_commit_transaction_no_booking_key():
    request_content = ('{vrq}{1}BARKER{2}AFFF{3}31{4}VIFGateway Test{5}3{8}108193016648!'
                       '{2}627{3}ExternalReference{4}10{1001}1'
                       '{1101}14{1102}Micropayment{1103}10{1106}Fred Nurk{1109}PayPal-0123456789{1111}1')

    response_content = '{vrp}{1}BARKER{2}AFFF{3}70141{5}Booking key is missing!'


@pytest.mark.skip(reason="WIP")
def test_vif_commit_micropayment_transaction():
    init_request_content = ('{vrq}{1}BARKER{2}D511{3}30{4}Request from DESKTOP-3MFAL8H using VIFGateway test utility v5.4.0{5}3{8}108193016648!'
                            '{1}627{2}VifTest{3}132498{4}1{10}10{11}1{13}11'
                            '{100001}1{100101}BOUNT00{100102}10{100103}1')

    init_response_content = ('{vrp}{1}BARKER{2}D511!'
                             '{p30}{3}Cinema 04{4}Cinema Four{5}PASSENGERS{6}Passengers{7}20170111100000{9}1{10}11'
                             '{1001}A 6{100001}1'
                             '{100101}BOUNT00{100103}10{100105}A 6{100106}Tkt Bounty Web{100108}1')

    commit_request_content = ('{vrq}{1}BARKER{2}D509{3}31{4}Request from DESKTOP-3MFAL8H using VIFGateway test utility v5.4.0{5}3{8}108193016648!'
                              '{2}627{4}11{5}ST-20170110-1955{1001}1'
                              '{1101}14{1102}Ticket Bounty{1103}11')

    commit_response_content = ('{vrp}{1}BARKER{2}D509!'
                               '{p31}{1}15563{2}1777975{3}ST-20170110-1955{4}2436551053'
                               '{1001}A 6{100001}1'
                               '{100101}BOUNT00{100103}10{100105}A 6{100106}Tkt Bounty Web{100107}2658299{100108}1{100110}Z0DJEAA2LGFLNV')


@pytest.mark.skip(reason="WIP")
def test_vif_init_transaction():
    init_request_content = ('{vrq}{1}NRLNGA{2}8edi{3}30{4}Ticket Bounty Init Transaction{5}3{8}108193016648!'
                            '{q30}{1}1769{2}tktbnty{3}93448{4}1{5}Ref9987{10}40{11}4.8{13}44.8{16}2253525874a5ac092d1{100001}4'
                            '{100101}BOUNT00{100102}10{100103}1.2'
                            '{100201}BOUNT00{100202}10{100203}1.2'
                            '{100301}BOUNT00{100302}10{100303}1.2'
                            '{100401}BOUNT00{100402}10{100403}1.2')

    init_response_content = ('{vrp}{1}NRLNGA{2}8edi!'
                             '{p30}{3}Cinema 03{4}Cinema Three{5}ROGUEONE{6}Rogue One: A Star Wars St{7}20170111104500{9}4.8{10}44.8'
                             '{1001}A 13{1002}A 12{1003}A 11{1004}A 10{100001}4'
                             '{100101}BOUNT00{100103}10{100105}A 13{100106}Tkt Bounty Web{100108}1.2'
                             '{100201}BOUNT00{100203}10{100205}A 12{100206}Tkt Bounty Web{100208}1.2'
                             '{100301}BOUNT00{100303}10{100305}A 11{100306}Tkt Bounty Web{100308}1.2'
                             '{100401}BOUNT00{100403}10{100405}A 10{100406}Tkt Bounty Web{100408}1.2')

    commit_request_content = ('{vrq}{1}NRLNGA{2}hfxm{3}31{4}Ticket Bounty Commit Transaction{5}3{8}108193016648!'
                              '{q31}{2}1769{4}44.80{5}42424XXXXXXX4242{7}0419925750{11}WWW{1001}1'
                              '{1101}4{1102}NAB{1103}44.80{1104}42424XXXXXXX4242{1105}{1106}Test at 2017-01-10 20:01:00 by Ticketbounty{1107}VISA{1108}{1109}47R839373V998061D{1111}1')

    commit_response_content = ('{vrp}{1}NRLNGA{2}hfxm!'
                               '{p31}{1}25395{2}1524202{3}42424XXXXXXX4242{4}7259352050{1001}A 13{1002}A 12{1003}A 11{1004}A 10{100001}4'
                               '{100101}BOUNT00{100103}10{100105}A 13{100106}Tkt Bounty Web{100107}2526568{100108}1.2{100110}Z0A5AUOPNW220U'
                               '{100201}BOUNT00{100203}10{100205}A 12{100206}Tkt Bounty Web{100207}2526569{100208}1.2{100210}Z03H1RVGH7YW9Q'
                               '{100301}BOUNT00{100303}10{100305}A 11{100306}Tkt Bounty Web{100307}2526570{100308}1.2{100310}Z0B1SLRS8EYCQ7'
                               '{100401}BOUNT00{100403}10{100405}A 10{100406}Tkt Bounty Web{100407}2526571{100408}1.2{100410}Z0H0G25J13FCB3')


@pytest.mark.skip(reason="WIP")
def test_vif_verify_booking():
    request_content = ('{vrq}{1}BARKER{2}5CCB{3}42{4}VIFGateway Test{8}108193016648!'
                       '{1}1554551020')

    response_content = ('{vrp}{1}BARKER{2}5CCB!'
                        '{p42}{1}15545{2}1777013{3}4242424242424242{4}1554551020{5}1{6}1{9}10{10}132417')


@pytest.mark.skip(reason="WIP")
def test_vif_collect_booking():
    request_content = ('{vrq}{1}BARKER{2}5CCA{3}32{4}VIFGateway Test{5}3{8}108193016648!'
                       '{1}1554551020{2}1')

    response_content = ('{vrp}{1}BARKER{2}5CCA!'
                        '{p32}{1}1777013{3}Cinema 02{4}Cinema Two{5}MOANA{6}Moana{7}20170110100000{10}10{11}15545{12}1777013{13}4242424242424242{14}1554551020{16}132417'
                        '{100001}1{100101}BOUNT00{100103}10{100105}D 17{100106}Tkt Bounty Web{100107}2656938{100110}Z0R6QCXLTMVMYP')
