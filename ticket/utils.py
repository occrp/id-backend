from ticket import constants

def split_open_tickets(tickets):
    o = []
    c = []
    if tickets and len(tickets) > 0:
        for t in tickets:
            (o if t.status in constants.OPEN_TICKET_STATUSES else c).append(t)
    return o, c

def smart_truncate(content, length):
    '''
    truncate a string, ending on a word break and adding ellipses
    '''
    if len(content) <= length:
        return content
    else:
        if ' ' in content[-20:]:
            return content[:length].rsplit(' ', 1)[0] + '...'
        else:  #if there is no word break, just do an ugly break
            return content[:length-3] + '...'

def get_actual_ticket(self):
    try:
        return self.personticket
    except:
        pass
    try:
        return self.companyticket
    except:
        pass
    try:
        return self.otherticket
    except:
        pass

def get_actual_tickets(tickets):
    actual_tickets = []

    for i in tickets:
        actual_tickets.append(get_actual_ticket(i))

    return actual_tickets
