# TicketCharges_to_ID2TicketCharges.py

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
sys.path.append(os.path.abspath("../../../"))
from ticket.models import *
from ticket.constants import *
from django.contrib.auth import get_user_model

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
        #print '+-- looking for user based on gkey: %s (%s)' % (value, profilegkeys[value])
        return get_user_model().objects.get(email=profilegkeys[value])
        #print '+-- found! id: %s' % value.id
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
        #print '+-- looking for ticket based on gkey: %s (%s)' % (value, ticketgkeys[value])
        return Ticket.objects.get(id=ticketgkeys[value])
        #print '+-- found! id: %s' % value.id
    except:
        missing_tickets.append(value)
        print('Ticket with old_google_key: "%s" does not seem to exist in %s; have you imported user data already?' % (value, ticket_gkeys_file))


def convert(in_file):
 
    f = open(in_file, 'r')
    reader = csv.reader(f)

    header_row = []
    entries = []

    tchrgs = []
    
    print "Setting up django..."
    django.setup()
    # grabbing the highest id in the TicketCharges database so as not to overwrite existing entries
    try:
        cnt = TicketCharge.objects.latest('id').id
    # in case we can't get it, just start with 0
    except:
        cnt = 0

    print "Harvesting from CSV: ",
    for row in reader:
        if not header_row:
            header_row = row
            continue

        cnt += 1

        tchrg = {"id": cnt}
        for i in range(len(row)):
            value = unicode(row[i], 'utf-8').strip()
            key = header_row[i]

            if key == 'paid_status':
                if value not in [ps[0] for ps in PAID_STATUS]:
                    value = 'unpaid'
            else:
                if value.strip() == 'False':
                    value = False
                elif value.strip() == 'True':
                    value = True

            # set the key
            tchrg[key] = value

        tchrgs.append(tchrg)

    print "... Got %d ticket charges\n" % (len(tchrgs))

    # stats
    ignored = {
      'user'   : 0,
      'ticket' : 0
    }
    i = 0
    for tchrg in tchrgs:
        i += 1
        print "\rAdding %20s ticket update data: %4d, a: (%16s, t: %16s)" % (tchrg["paid_status"], i, tchrg["user"], tchrg["ticket"]),
        sys.stdout.flush()
        
        # the model
        t = TicketCharge()

        for key, value in tchrg.iteritems():
            #print '+-- working on: %24s' % key
            # this has to be a Profile instance
            # or, actually, anything that we use as the User model these days
            if key == "user":
                value = get_user_profile(value)
                # did we actually get anything?
                if not value:
                    # no. break -- this will make the else part of the for not execute
                    print("\n     +-- ignoring this ticket charge due to missing user! you'll find all missing user gkeys in %s" % user_missing_file)
                    ignored['user'] += 1
                    break
            # this has to be a Ticket instance
            elif key == "ticket":
                value = get_ticket(value)
                # did we actually get anything?
                if not value:
                    # no. break -- this will make the else part of the for not execute
                    print("\n     +-- ignoring this ticket charge due to missing ticket! you'll find all missing ticket gkeys in %s" % ticket_missing_file)
                    ignored['ticket'] += 1
                    break
            elif key in ['created', 'reconciled_date']:
                #print '     +-- value is: %s' % value
                if not value.strip():
                    continue
            # set the attribute
            setattr(t, key, value)
            
        # this will execute *only* if the for loop terminated normally
        else:
            # databasing the database
            try:
                # save the ticket
                t.save()
                #print '+-- created         : %s' % t.created
                #print '+-- reconciled_date : %s' % t.created
            # wat.
            except IntegrityError, e:
                print "Skipping dupe: %s" % (e)
      
    print "\rAdding ticket updates: Done.                                                              "
    print "\n+-- processed %d individual ticket charges" % (i)
    print   "    +-- ignored %d ticket charges due to missing user data" % (ignored['user'])
    print   "    +-- ignored %d ticket charges due to missing ticket data" % (ignored['ticket'])


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
  
    print "Loading gkeys from %s, %s..." % (user_gkeys_file, ticket_gkeys_file)
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

    # users known to be missing
    print "Loading missing user gkeys..."
    try:
        with open(ticket_missing_file, 'rb') as missingfile:
            missing_tickets = pickle.load(missingfile)
        print '+-- loaded %d missing user gkeys from %s' % (len(missing_tickets), ticket_missing_file)
    except:
        print "+-- warning, no missing user gkeys loaded, tried from %s." % ticket_missing_file
    
    
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