# TicketUpdates_to_ID2TicketUpdates.py

import sys
import getopt
import csv
from os.path import dirname
import os
import json
from django.db.utils import IntegrityError
import django
import pickle

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.settings")
sys.path.append(os.path.abspath("../../"))
from ticket.models import *
from django.contrib.auth import get_user_model;

missing_users = []
missing_tickets = []

# getting a user profile from the db based on gkeys, using profilegkeys
def get_user_profile(value):
    # known-missing?
    if value in missing_users:
        print('User with old_google_key: "%s" does not seem to exist in %s; have you imported user data already?' % (value, user_gkeys_file))
        return None
    # should be known, try getting it from the db
    try:
        # try the db using profilegkeys
        print '+-- looking for user based on gkey: %s (%s)' % (value, profilegkeys[value])
        return get_user_model().objects.get(email=profilegkeys[value])
        print '+-- found! id: %s' % value.id
    except:
        missing_users.append(value)
        print('User with old_google_key: "%s" does not seem to exist in %s; have you imported user data already?' % (value, user_gkeys_file))
        return None

# getting a ticket from the db based on gkeys, using ticketgkeys
def get_ticket(value):
    # known-missing?
    if value in missing_tickets:
        print('Ticket with old_google_key: "%s" does not seem to exist in %s; have you imported user data already?' % (value, ticket_gkeys_file))
        return None
    # should be known, try getting it from the db
    try:
        # try the db using profilegkeys
        print '+-- looking for ticket based on gkey: %s (%s)' % (value, ticketgkeys[value])
        return Ticket.objects.get(id=ticketgkeys[value])
        print '+-- found! id: %s' % value.id
    except:
        missing_tickets.append(value)
        print('Ticket with old_google_key: "%s" does not seem to exist in %s; have you imported user data already?' % (value, ticket_gkeys_file))


def convert(in_file):
 
    f = open(in_file, 'r')
    reader = csv.reader(f)

    header_row = []
    entries = []
    cnt = 0

    tupdts = []

    print "Harvesting from CSV: ",
    for row in reader:
        if not header_row:
            header_row = row
            continue

        cnt += 1

        tupdt = {"id": cnt}
        for i in range(len(row)):
            value = unicode(row[i], 'utf-8').strip()
            key = header_row[i]

            # extra_relation is kill
            if key == 'extra_relation':
                continue
            # set the key
            tupdt[key] = value

        tupdts.append(tupdt)

    print "... Got %d ticket updates" % (cnt - 1)
    print "Setting up django..."
    django.setup()

    i = 0
    for tupdt in tupdts:
        i += 1
        print("Adding %20s ticket update data: %4d, a: (%s, t: %s)" % (tupdt["update_type"], i, tupdt["author"], tupdt["ticket"]))
        
        # the model
        t = TicketUpdate()

        for key, value in tupdt.iteritems():
            print '+-- working on: %24s' % key
            # this has to be a Profile instance
            # or, actually, anything that we use as the User model these days
            if key == "author":
                value = get_user_profile(value)
                # did we actually get anything?
                if not value:
                    # no. break -- this will make the else part of the for not execute
                    print("+-- ignoring this ticket update due to missing user! you'll find all missing user gkeys in %s" % user_missing_file)
                    break
            # this has to be a Ticket instance
            elif key == "ticket":
                value = get_ticket(value)
                # did we actually get anything?
                if not value:
                    # no. break -- this will make the else part of the for not execute
                    print("+-- ignoring this ticket update due to missing ticket! you'll find all missing ticket gkeys in %s" % ticket_missing_file)
                    break
            # set the attribute
            setattr(t, key, value)
            
        # this will execute *only* if the for loop terminated normally
        else:
            # databasing the database
            try:
                # save the ticket
                t.save()
                print '+-- created        : %s' % t.created
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
    workdir = os.path.dirname(os.path.abspath(in_file))
    
    user_gkeys_file = os.path.join(workdir, 'UserProfile.gkeys')
    user_missing_file = os.path.join(workdir, 'UserProfile.missing')
    ticket_gkeys_file = os.path.join(workdir, 'Ticket.gkeys')
    ticket_missing_file = os.path.join(workdir, 'Ticket.missing')
  
    print "Loading gkeys..."
    try:
        with open(user_gkeys_file, 'rb') as gkeyfile:
            profilegkeys = pickle.load(gkeyfile)
        print '+-- loaded %d UserProfile gkeys from %s' % (len(profilegkeys), user_gkeys_file)
        with open(ticket_gkeys_file, 'rb') as gkeyfile:
            ticketgkeys = pickle.load(gkeyfile)
        print '+-- loaded %d Ticket gkeys from %s' % (len(ticketgkeys), ticket_gkeys_file)
    except:
        print "+-- error, no gkeys loaded! you kind of need them, though..."
        sys.exit(1)
    
    # users known to be missing
    print "Loading missing user gkeys..."
    try:
        with open(user_missing_file, 'rb') as missingfile:
            missing_users = pickle.load(missingfile)
        print '+-- loaded %d missing user gkeys from %s' % (len(missing_users), user_missing_file)
    except:
        print "+-- warning, no missing user gkeys loaded, tried from %s." % user_missing_file
    
    
    convert(in_file)

  
    # saving missing users, if any
    if missing_users:
        try:
            with open(user_missing_file, 'wb') as missingfile:
                pickle.dump(missing_users, missingfile)
            print "Dumped %d missing user gkeys to %s." % (len(missing_users), user_missing_file)
        except:
            print 'Dumping %d missing user gkeys to %s has failed!..' % (len(missing_users), user_missing_file)
            
    # saving missing tickets, if any
    if missing_tickets:
        try:
            with open(ticket_missing_file, 'wb') as missingfile:
                pickle.dump(missing_tickets, missingfile)
            print "Dumped %d missing ticket gkeys to %s." % (len(missing_tickets), ticket_missing_file)
        except:
            print 'Dumping %d missing ticket gkeys to %s has failed!..' % (len(missing_tickets), ticket_missing_file)