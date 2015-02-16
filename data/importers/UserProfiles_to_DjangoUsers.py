# UserProfiles_to_DjangoUsers.py

import sys
import getopt
import csv
from os.path import dirname
import os
import json
from django.db.utils import IntegrityError

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
sys.path.append(os.path.abspath("../../"))
from id.models import *


def convert(in_file):
    f = open(in_file, 'r')
    reader = csv.reader(f)

    header_row = []
    entries = []
    cnt = 1

    users = []
    profiles = []

    print "Harvesting from CSV: ",
    for row in reader:
        if not header_row:
            header_row = row
            continue

        cnt += 1

        user = {"id": cnt}
        profile = {"user_id": cnt}
        for i in range(len(row)):
            value = row[i]
            key = header_row[i]

            if key == "user":
                pass
            elif key == "email":
                user["username"] = value
                user["email"] = value
                profile["email"] = value
            elif key == "id":
                profile["old_google_id"] = value
            else:
                profile[key] = value

        users.append(user)
        profiles.append(profile)

    print "... Got %d users" % (cnt - 1)

    i = 0
    for user in users:
        i += 1
        print "\rAdding users: %d" % i,
        sys.stdout.flush()
        u = User()
        u.id = user["id"]
        u.username = user["username"]
        try:
            u.save()
        except IntegrityError, e:
            print "Skipping dupe: %s" % (e)
    print "\rAdding users: Done."

    i = 0
    for profile in profiles:
        i += 1
        print "\rAdding profiles: %d" % i,
        sys.stdout.flush()
        p = Profile()
        for key, value in profile.iteritems():
            setattr(p, key, value)
        try:
            p.save()
        except IntegrityError, e:
            print "Skipping dupe: %s" % (e)
    print "\rAdding profiles: Done."



if __name__ == "__main__":
    try:
        script, input_file_name = sys.argv
    except ValueError:
        print "\nRun via:\n\n%s input_file_name" % sys.argv[0]
        sys.exit()

    in_file = input_file_name
    convert(in_file)
