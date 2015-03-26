# UserProfiles_to_DjangoUsers.py

import sys
import getopt
import csv
from os.path import dirname
import os
import json
from django.db.utils import IntegrityError
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.settings")
sys.path.append(os.path.abspath("../../"))
from id.models import *


def convert(in_file):
    f = open(in_file, 'r')
    reader = csv.reader(f)

    header_row = []
    entries = []
    cnt = 1

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

            if key == "user":
                pass
            elif key == "id":
                user["old_google_id"] = value
            else:
                user[key] = value

        users.append(user)

    print "... Got %d users" % (cnt - 1)
    print "Setting up django..."
    django.setup()

    i = 0
    for user in users:
        i += 1
        print "\rAdding user profiles: %4d, %64s" % (i, user["email"]),
        sys.stdout.flush()
        u = Profile()
        u.is_superuser = user["is_admin"]
        for key, value in user.iteritems():
            setattr(u, key, value)
        try:
            u.save()
        except IntegrityError, e:
            print "Skipping dupe: %s" % (e)
    print "\rAdding user profiles: Done."



if __name__ == "__main__":
    try:
        script, input_file_name = sys.argv
    except ValueError:
        print "\nRun via:\n\n%s input_file_name" % sys.argv[0]
        sys.exit()

    in_file = input_file_name
    convert(in_file)
