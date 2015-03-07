####
#
#  Podaci shell. To use, run with 'python shell.py' from Podaci folder.
#
#  Gives a nice little superuser interface to the Podaci datastore.
#
####
import os
import sys
import cmd
import glob
from datetime import datetime
import dateutil.parser
from argparse import ArgumentParser
sys.path.append("../")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.settings")

import django
from settings.settings import *
from podaci.filesystem import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

django.setup()

def getuser(u):
    if not u.isdigit():
        try:
            user = User.objects.get(username=u)
        except:
            print "Error: User %s does not exist" % u
            return None
    else:
        try:
            user = User.objects.get(id=u)
        except:
            print "Error: User %s does not exist" % u
            return None
    return user


class PodaciShell(cmd.Cmd):
    """Simple command processor example."""
    prompt = 'podaci> '

    def __init__(self):
        cmd.Cmd.__init__(self)
        username = raw_input("Username? ")
        password = raw_input("Password? ")

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                print("User is valid, active and authenticated")
            else:
                print("The password is valid, but the account has been disabled!")
                sys.exit()
        else:
            print("The username and password were incorrect.")
            sys.exit()

        self.fs = FileSystem(
            PODACI_SERVERS, PODACI_ES_INDEX, 
            PODACI_FS_ROOT, user)

    def do_tags(self, line):
        params = line.split(" ")
        count, tags = self.fs.list_tags()

        if "-l" in params:
            print "%-30s %-20s %-12s %s" % ("Name", "ID", "Added", "Pub User Writ Note Files")
            for tag in tags:
                date = dateutil.parser.parse(tag["date_added"])
                print "%-30s %-20s %-12s   %s" % (tag["name"], tag.id, date.strftime("%Y-%m-%d"), tag.details_string())
        else:
            for tag in tags:
                print tag.meta["name"]
        print "%d tags" % count

    def do_ls(self, line):
        params = line.split(" ")
        details = "-l" in params
        if details:
            params.remove("-l")

        tag = params[0]
        count, files = self.fs.list_files(tag)
        if details:
            print "%-30s %-20s %-12s %s" % ("Name", "ID", "Added", "Pub User Writ Note Files")
            for f in files:
                date = dateutil.parser.parse(f["date_added"])
                print "%-30s %-20s %-12s   %s" % (f["name"], f.id, date.strftime("%Y-%m-%d"), f.details_string())
        else:
            for f in files:
                print f.meta["name"]

        print "%d files" % count

    def do_add(self, line):
        params = line.split(" ")
        for f in params:
            if not os.path.isfile(f):
                print "%s does not exist" % f

        for f in params:
            fid, fi, s = self.fs.create_from_file(f)
            if s:
                print "%s" % fid
            else:
                print "Could not create file %s." % f

    def complete_add(self, text, line, begidx, endidx):
        params = line.split(" ")
        return glob.glob(params[-1]+'*')

    def do_tag(self, line):
        params = line.split(" ")
        fileids = []
        addtags = []
        rmtags = []
        for p in params:
            if p[0] == "@":
                fileids.append(p[1:])
            elif p[0] == "+":
                addtags.append(p[1:])
            elif p[0] == "-":
                rmtags.append(p[1:])
            else:
                print "Error: Parameters must start with @, + or -."
                self.help_tag()
                return

        # FIXME: Verify that the tags exist.
        for f in fileids:
            fh = self.fs.get_file_by_id(f)

            for t in addtags:
                fh.add_tag(t)

            for t in rmtags:
                fh.remove_tag(t)

    def help_tag(self):
        print "Usage: tag @file1 @file2 @file3 +tag1 +tag2 -tag3"
        print "This will add tags tag1 and tag2 to the three files, and remove tag3"

    def do_perm(self, line):
        params = line.split(" ")
        fileids = []
        addusers = []
        rmusers = []
        make_public = False
        make_private = False
        give_write = False

        for p in params:
            if p == "--write":
                give_write = True
                continue
            if p == "--public":
                make_public = True
                continue
            if p == "--private":
                make_private = True
                continue

            if p[0] == "@":
                fileids.append(p[1:])
            elif p[0] == "+":
                u = getuser(p[1:])
                if u:
                    addusers.append(u)
                else:
                    return
            elif p[0] == "-":
                u = getuser(p[1:])
                if u:
                    rmusers.append(u)
                else:
                    return
            else:
                print "Error: Parameters must start with @, + or -."
                self.help_perm()
                return

        if make_public and make_private:
            print "Error: You can't both make files public and private!"
            return

        for f in fileids:
            fh = self.fs.get_file_by_id(f)
            for u in addusers:
                fh.add_user(u, give_write)

            for u in rmusers:
                fh.remove_user(u)

            if make_public:
                fh.make_public()
            elif make_private:
                fh.make_private()

    def do_log(self, line):
        params = line.split(" ")
        fileids = []
        for p in params:
            if p[0] == "@":
                fh = self.fs.get_file_by_id(p[1:])
                print "=== Log for %s ===" % p[1:]
                for line in fh["changelog"]:
                    print "[%s] %s :: %s" % (line["date"], line["user"], line["message"])


    def help_perm(self):
        print "Usage: tag [-w] @file1 @file2 @file3 +user1 +user2 -user3"
        print "This will allow users user1 and user2 to access the three files, and disallow user3"
        print "  --write    Gives them write permission"
        print "  --public   Makes the files public"
        print "  --private  Makes the files not public"

    def do_exit(self, line):
        return True
    
    def do_EOF(self, line):
        return True

if __name__ == '__main__':
    PodaciShell().cmdloop()