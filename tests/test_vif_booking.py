import pytest

from venue.vif_message import VIFMessage
from venue.vif_gateway import VIFGateway
from venue.vif_ticket_array import VIFTicketArray


def test_vif_handshake(monkeypatch):
    def mocksend(self, message):
        return message
    monkeypatch.setattr(VIFGateway, 'send', mocksend)
    # Initialise gateway class
    gateway = VIFGateway(site_name='BARKER', host='127.0.0.1',
                         auth_key='1081930166', agent_no='48')
    # Add 3 tickets to array
    ticket_array = VIFTicketArray()
    ticket_array.add_ticket(ticket_code='BOUNT00', price=5, service_fee=1)
    ticket_array.add_ticket(ticket_code='BOUNT00', price=5, service_fee=1)
    ticket_array.add_ticket(ticket_code='BOUNT00', price=5, service_fee=1)
    # Hijack sending init_transaction message so we can inspect its contents
    message = gateway.init_transaction(
        workstation_id='123', user_code='TKTBTY', session_no='999',
        transaction_type=1, customer_reference='CUSTNO123',
        ticket_array=ticket_array)
    expected = {
        '1': '123',             # workstation id
        '2': 'TKTBTY',          # user code
        '3': '999',             # session number
        '4': 1,                 # transaction type
        '5': 'CUSTNO123',       # customer reference
        '10': 15,               # total ticket prices
        '11': 3,                # total ticket fees
        '13': 18,               # total transaction price
        '100001': 3,            # elements in ticket array
        '100101': 'BOUNT00',    # ticket code (1)
        '100102': 5,            # ticket price (1)
        '100103': 1,            # ticket service fee (1)
        '100201': 'BOUNT00',    # ticket code (2)
        '100202': 5,            # ticket price (2)
        '100203': 1,            # ticket service fee (3)
        '100301': 'BOUNT00',    # ticket code (3)
        '100302': 5,            # ticket price (2)
        '100303': 1             # ticket service fee (3)
    }
    assert expected == message.body_dict()
