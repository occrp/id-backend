# Tickets_to_ID2Tickets.py

import sys
import getopt
import csv
from os.path import dirname
import os
import json
from django.db.utils import IntegrityError
import django
from ast import literal_eval

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.settings")
sys.path.append(os.path.abspath("../../"))
from ticket.models import *
from django.contrib.auth import get_user_model;

# we're gonna need that...
import re

def convert(in_file):
 
    f = open(in_file, 'r')
    reader = csv.reader(f)

    header_row = []
    entries = []
    cnt = 1

    tickets = []

    print "Harvesting from CSV: ",
    for row in reader:
        if not header_row:
            header_row = row
            continue

        cnt += 1

        ticket = {"id": cnt}
        for i in range(len(row)):
            value = unicode(row[i], 'utf-8').strip()
            key = header_row[i]

            # id, entities, flagged are kill
            if key in ("id", "entities", "flagged"):
                pass
            # let's properly handle the ticket type
            elif key == "ticket_type":
                if 'PersonTicket' in value:
                    value = 'person_ownership'
                elif 'CompanyTicket' in value:
                    value = 'company_ownership'
                elif 'Other' in value:
                    value = 'other'
                else:
                    raise ValueError('%s is not a valid ticket type' % value)
            # that one's tricky, but luckily literal_eval comes to rescue
            elif key == "family":
                if value == '':
                    value = []
                else:
                    # get the eval'd value
                    oldvalue = literal_eval(value)
                    value = []
                    # we have a few empty values, handle these
                    if type(oldvalue) != list:
                        oldvalue = [oldvalue]
                    for v in oldvalue:
                        if v.strip() != '':
                            value.append(v)
                            
            # maybe it's a True/False string?
            else:
                # we have to handle "True"/"False" properly
                if value == 'False':
                    value = False
                elif value == 'True':
                    value = True
            # set the key
            ticket[key] = value

        tickets.append(ticket)

    print "... Got %d tickets" % (cnt - 1)
    print "Setting up django..."
    django.setup()

    # we need that regex for the 'responders' field
    r = re.compile("u'UserProfile', (\d+)L, _app")

    i = 0
    for ticket in tickets:
        i += 1
        print("Adding %20s ticket data: %4d, %s %s" % (ticket["ticket_type"], i, ticket["family"], type(ticket["family"])))
        
        # which kind of ticket are we working with?
        if ticket['ticket_type'] == 'person_ownership':
            t = PersonTicket()
        elif ticket['ticket_type'] == 'company_ownership':
            t = CompanyTicket()
        elif ticket['ticket_type'] == 'other':
            t = OtherTicket()
        
        responders = ''
        volunteers = ''
        for key, value in ticket.iteritems():
            print '+-- working on: %24s' % key
            #sys.stdout.flush()
            # this has to be a Profile instance
            # or, actually, anything that we use as the User model these days
            if key == "requester":
                try:
                    value = get_user_model().objects.get(old_google_key=value)
                except:
                    print('User with old_google_key: "%s" does not seem to exist; have you imported user data already?' % value)
                    sys.exit(1)
            # we don't need time here
            elif key == 'deadline':
                value = value.strip()[:10]
            elif key == "responders":
                # we're not going to save that into the ticket directly
                # instead, we're saving it for use after the ticket is saved
                responders = value
                continue
            elif key == "volunteers":
                # we're not going to save that into the ticket directly
                # instead, we're saving it for use after the ticket is saved
                volunteers = value
                continue
            # set the attribute
            setattr(t, key, value)
        
        # databasing the database
        try:
            # save the ticket
            t.save()
            # handle responders...
            print('Responders: "%s"' % responders)
            for resp in r.finditer(responders):
                print '+-- %s' % resp.group(1)
                u = get_user_model().objects.get(old_google_key=resp.group(1))
                t.responders.add(u)
            # ...and volunteers
            print('Volunteers: "%s"' % volunteers)
            for vol in r.finditer(volunteers):
                print '+-- %s' % vol.group(1)
                u = get_user_model().objects.get(old_google_key=vol.group(1))
                t.volunteers.add(u)
        # wat.
        except IntegrityError, e:
            print "Skipping dupe: %s" % (e)
      
    print "\rAdding tickets: Done."


if __name__ == "__main__":
    try:
        script, input_file_name = sys.argv
    except ValueError:
        print "\nRun via:\n\n%s input_file_name" % sys.argv[0]
        sys.exit()

    in_file = input_file_name
    convert(in_file)
