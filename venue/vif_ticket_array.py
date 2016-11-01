class VIFTicketArray(object):
    def __init__(self):
        self._tickets = []

    def add_ticket(self, ticket_code, price, service_fee=0, seat_name=None):
        ticket = {
            'ticket_code': ticket_code,
            'price': price,
            'service_fee': service_fee,
            'seat_name': seat_name
        }
        self._tickets.append(ticket)

    def count(self):
        return len(self._tickets)

    def _total_ticket_field(self, field):
        total = 0
        for ticket in self._tickets:
            total += ticket.get(field, 0)
        return total

    def total_ticket_prices(self):
        return self._total_ticket_field('price')

    def total_ticket_fees(self):
        return self._total_ticket_field('service_fee')

    def total(self):
        return self.total_ticket_prices() + self.total_ticket_fees()

    def dict(self):
        array = list(enumerate(self._tickets, start=1))
        d = {}
        for i, ticket in array:
            key = 100000 + i * 100
            if ticket.get('ticket_code'):
                d[str(key + 1)] = ticket['ticket_code']
            if ticket.get('price'):
                d[str(key + 2)] = ticket['price']
            if ticket.get('service_fee'):
                d[str(key + 3)] = ticket['service_fee']
            if ticket.get('seat_name'):
                d[str(key + 4)] = ticket['seat_name']
        return d
