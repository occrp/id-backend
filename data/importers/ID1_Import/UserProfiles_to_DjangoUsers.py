# UserProfiles_to_DjangoUsers.py

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
from id.models import *


def convert(in_file):
    f = open(in_file, 'r')
    reader = csv.reader(f)

    header_row = []
    entries = []
    cnt = 1 # starting at id=2 so that a pre-existing admin account won't cause a conflict

    users = []
    
    # needed for verification
    all_emails = []

    print "Harvesting from CSV: ",
    for row in reader:
        if not header_row:
            header_row = row
            continue

        cnt += 1

        user = {"id": cnt}
        for i in range(len(row)):
            value = unicode(row[i], 'utf-8').strip()
            key = header_row[i]

            # user and is_for_profit are kill.
            if key in ("user", "is_for_profit"):
                continue
            # this is the internal ID from bigtable
            # will *not* be saved in the database; instead, will land in
            # UserProfile.gkeys for reference while importing Tickets and TicketUpdates
            elif key == "key":
                user["old_google_key"] = value
                print '\rold_google_key : %s' % value,
                sys.stdout.flush()
                continue
            # let's make sure e-mail is lower-case, shall we?
            elif key == "email":
                value = value.lower()
            # we have to handle "True"/"False" properly
            else:
                if value == 'False':
                    value = False
                elif value == 'True':
                    value = True
            # set the key
            user[key] = value

        # working array
        users.append(user)
        # verification array
        if user['email'] not in all_emails:
            all_emails.append(user['email']);

    print "... Got %d users" % (cnt - 1)
    print "Setting up django..."
    django.setup()

    i = 0
    gkeys = {}
    for user in users:
        i += 1
        print "\rAdding user profiles: %4d, %64s" % (i, user["email"]),
        sys.stdout.flush()
        u = Profile()
        u.is_superuser = user["is_admin"]
        for key, value in user.iteritems():
            # we don't want to save old_google_key into the db
            # rather, to gkeys, so that it's pickled into UserProfile.gkeys for further reference
            if key == 'old_google_key':
                gkeys[value] = user['email']
                continue
            # set the attrs we actually *want* to set
            setattr(u, key, value)
        # save the user profile to the db
        try:
            u.save()
        except IntegrityError, e:
            print "Skipping dupe: %s" % (e)
            
    print "\rAdding user profiles: Done."
    
    # verify all e-mails found their wait into the database
    print "Verifying all emails have in fact been properly imported..."
    failed_emails = []
    for email in all_emails:
        print '\r+-- checking: %60s...' % email,
        sys.stdout.flush()
        try:
            u = Profile.objects.get(email=email)
            if not u:
                failed_emails.append(email)
                print '     +-- warning: not in database!'
        except e:
            print('+-- whoops, we have an exception: %s' % e)
    if failed_emails:
        print('\rEmail verification failed in %d instances.' % len(failed_emails))
    else:
        print('\rEmail verification passed.')
    
    # we need to save the old_google_key-related data
    try:
        with open(user_gkeys_file, 'wb') as gkeysfile:
            pickle.dump(gkeys, gkeysfile)
        print "Dumped %d gkeys to %s." % (len(gkeys), user_gkeys_file)
    except:
        print 'Dumping %d gkeys to %s has failed! You kind of need them for ticket import...' % (len(gkeys), user_gkeys_file)


if __name__ == "__main__":
    
    try:
        script, input_file_name = sys.argv
    except ValueError:
        print "\nRun via:\n\n%s input_file_name" % sys.argv[0]
        sys.exit()

    in_file = input_file_name
    workdir = os.path.dirname(os.path.abspath(in_file))
    
    user_gkeys_file = os.path.join(workdir, 'UserProfile.gkeys')
    
    convert(in_file)