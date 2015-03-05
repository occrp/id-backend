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
from datetime import datetime
import dateutil.parser
from argparse import ArgumentParser
sys.path.append("../")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.settings")

from settings.settings import *
from podaci.filesystem import *

class Strawman:
    def __init__(self, id, username):
        self.id = id
        self.username = username

class PodaciShell(cmd.Cmd):
    """Simple command processor example."""
    prompt = 'podaci> '

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.fs = FileSystem(
            PODACI_SERVERS, PODACI_ES_INDEX, 
            PODACI_FS_ROOT, Strawman('0', 'Podaci superuser'))

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
        if "-l" in params:
            print "%-30s %-20s %-12s %s" % ("Name", "ID", "Added", "Pub User Writ Note Files")
            for f in files:
                date = dateutil.parser.parse(f["date_added"])
                print "%-30s %-20s %-12s   %s" % (f["name"], f.id, date.strftime("%Y-%m-%d"), f.details_string())
        else:
            for f in files:
                print f.meta["name"]

        print "%d files" % count
    
    def do_EOF(self, line):
        return True

if __name__ == '__main__':
    PodaciShell().cmdloop()