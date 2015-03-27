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
from id.models import *


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
            # that one's tricky, but luckily literal_eval comes to resque
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

    i = 0
    for ticket in tickets:
        i += 1
        print("Adding %20s ticket data: %4d, %s %s" % (ticket["ticket_type"], i, ticket["family"], type(ticket["family"])))
        #sys.stdout.flush()
        
        # which kind of ticket are we working with?
        """t = Ticket()
        
        u.is_superuser = user["is_admin"]
        for key, value in user.iteritems():
            setattr(u, key, value)
        try:
            u.save()
        except IntegrityError, e:
            print "Skipping dupe: %s" % (e)
    print "\rAdding user profiles: Done."
    """



if __name__ == "__main__":
    try:
        script, input_file_name = sys.argv
    except ValueError:
        print "\nRun via:\n\n%s input_file_name" % sys.argv[0]
        sys.exit()

    in_file = input_file_name
    convert(in_file)
