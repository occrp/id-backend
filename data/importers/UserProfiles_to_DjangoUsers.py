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
    cnt = 0

    users = []

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
                pass
            # this is the internal ID from bigtable
            # will *not* be saved in the database; instead, will land in
            # UserProfile.gkeys for reference while importing Tickets and TicketUpdates
            elif key == "key":
                user["old_google_key"] = value
                print('old_google_key : %s' % value)
            # we have to handle "True"/"False" properly
            else:
                if value == 'False':
                    value = False
                elif value == 'True':
                    value = True
                # set the key
                user[key] = value

        users.append(user)

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
    
    # we need to save the old_google_key-related data
    try:
        with open('UserProfile.gkeys', 'wb') as gkeysfile:
            pickle.dump(gkeys, gkeysfile)
        print "Dumped %d gkeys." % len(gkeys)
    except:
        print 'Dumping %d gkeys has failed! You kind of need them for ticket import...' % len(gkeys)


if __name__ == "__main__":
    try:
        script, input_file_name = sys.argv
    except ValueError:
        print "\nRun via:\n\n%s input_file_name" % sys.argv[0]
        sys.exit()

    in_file = input_file_name
    convert(in_file)
