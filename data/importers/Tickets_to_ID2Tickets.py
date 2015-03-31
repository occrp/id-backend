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
import pickle
import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.settings")
sys.path.append(os.path.abspath("../../"))
from ticket.models import *
from django.contrib.auth import get_user_model;

# we're gonna need that...
import re

missing_users = []

# getting a user profile from the db based on gkeys, using profilegkeys
def get_user_profile(value):
    # known-missing?
    if value in missing_users:
        print('User with old_google_key: "%s" does not seem to exist in UserProfile.gkeys; have you imported user data already?' % value)
        return None
    # should be known, try getting it from the db
    try:
        # try the db using profilegkeys
        print '+-- looking for user based on gkey: %s (%s)' % (value, profilegkeys[value])
        return get_user_model().objects.get(email=profilegkeys[value])
        print '+-- found! id: %s' % value.id
    except:
        missing_users.append(value)
        print('User with old_google_key: "%s" does not seem to exist in UserProfile.gkeys; have you imported user data already?' % value)
        return None


def convert(in_file):
 
    f = open(in_file, 'r')
    reader = csv.reader(f)

    header_row = []
    entries = []
    cnt = 0

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
            # this is the internal ID from bigtable
            # will *not* be saved in the database; instead, will land in
            # UserProfile.gkeys for reference while importing Tickets and TicketUpdates
            elif key == "key":
                ticket["old_google_key"] = value
                print('old_google_key : %s' % value)
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
    gkeys = {}
    for ticket in tickets:
        i += 1
        print("Adding %20s ticket data: %4d, %s (old key: %s)" % (ticket["ticket_type"], i, ticket["name"], ticket["key"]))
        
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
            # this has to be a Profile instance
            # or, actually, anything that we use as the User model these days
            if key == "requester":
                # get user's profile even if it was a dupe and not got included in the db
                value = get_user_profile(value)
                # did we actually get anything?
                if not value:
                    # no. break -- this will make the else part of the for not execute
                    print("+-- ignoring this ticket update due to missing user! you'll find all missing user gkeys in UserProfile.missing")
                    break
            # we don't need time here
            elif key in ['deadline', 'dob']:
                value = value.strip()[:10]
                # and we definitely don't need empty dates
                if not value:
                    continue
            # need to pay special attention to dates
            elif key in ['created', 'status_updated']:
                print '     +-- value: %s' % value
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
            # we don't want to save old_google_key into the db
            # rather, to gkeys, so that it's pickled into UserProfile.gkeys for further reference
            if key == 'old_google_key':
                gkeys[value] = ticket['id']
                print '     +-- gkey / id : %s / %d' % (value, ticket['id'])
                continue
            # set the attribute
            setattr(t, key, value)
        
        # this will get executed if *and only* if the for loop terminated normally (i.e. no "break")
        # that way we can skip entries with missing data
        else:
            # fix status_updated
            if not t.status_updated:
                t.status_updated = datetime.datetime.strptime(t.created, '%Y-%m-%d %H:%M:%S.%f')
                print '+-- t.status_updated set to t.created : %s' % t.status_updated
            # databasing the database
            try:
                # save the ticket
                t.save()
                print '+-- ticket id / db id : %d / %d' % (ticket['id'], t.id)
                print '+-- created           : %s' % t.created
                print '+-- status_updated    : %s' % t.status_updated
                # handle responders...
                print('Responders: "%s"' % responders)
                for resp in r.finditer(responders):
                    print '+-- %s' % resp.group(1)
                    u = get_user_profile(resp.group(1))
                    if u:
                        t.responders.add(u)
                    else:
                        print('     +-- missing, noted')
                # ...and volunteers
                print('Volunteers: "%s"' % volunteers)
                for vol in r.finditer(volunteers):
                    print '+-- %s' % vol.group(1)
                    u = get_user_profile(vol.group(1))
                    if u:
                        t.volunteers.add(u)
                    else:
                        print('     +-- missing, noted')
            # wat.
            except IntegrityError, e:
                print "Skipping dupe: %s" % (e)
      
    print "\rAdding tickets: Done."
    
    # we need to save the old_google_key-related data
    try:
        with open('Ticket.gkeys', 'wb') as gkeysfile:
            pickle.dump(gkeys, gkeysfile)
        print "Dumped %d gkeys." % len(gkeys)
    except:
        print 'Dumping %d gkeys has failed! You kind of need them for ticket updates import...' % len(gkeys)


if __name__ == "__main__":
  
    print "Loading gkeys..."
    try:
        with open('UserProfile.gkeys', 'rb') as gkeyfile:
            profilegkeys = pickle.load(gkeyfile)
        print '+-- loaded %d UserProfile gkeys' % len(profilegkeys)
    except:
        print "+-- error, no gkeys loaded! you kind of need them, though..."
        sys.exit(1)
  
    try:
        script, input_file_name = sys.argv
    except ValueError:
        print "\nRun via:\n\n%s input_file_name" % sys.argv[0]
        sys.exit()

    in_file = input_file_name
    convert(in_file)
    
    # saving missing users, if any
    if missing_users:
        try:
            with open('UserProfiles.missing', 'wb') as missingfile:
                pickle.dump(missing_users, missingfile)
            print "Dumped %d missing user gkeys to `UserProfiles.missing`." % len(missing_users)
        except:
            print 'Dumping %d missing user gkeys has failed!..' % len(gkeys)
