# http://occrp-elasticsearch-1:9200/id_prod/_search/
import sys
import os
import time
import json
from datetime import datetime
sys.path.append("../../")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.settings")

import elasticsearch
import urllib2
import threading
from podaci.filesystem import *

OLD_SERVERS = [{"host": "54.227.243.186"}]
OLD_ES_INDEX = "id_prod"
OLD_DATA_ROOT = "/home/datatrac/indexed/public"

NEW_SERVERS = [{"host": "localhost"}]
NEW_ES_INDEX = "podaci"
NEW_DATA_ROOT = "/home/smari/Projects/OCCRP/data/"

class Strawman:
    def __init__(self, id, username):
        self.id = id
        self.username = username


class OldESImporter:
    def __init__(self):
        self.old_es = elasticsearch.Elasticsearch(OLD_SERVERS, retry_on_timeout=True)
        self.fs = FileSystem(NEW_SERVERS, NEW_ES_INDEX, NEW_DATA_ROOT, 
            Strawman("1000000001", "OldElasticSearchImporterBot"))
        self.tagcache = self.fs.get_tag_dict()
        if "Imported from old Datavault" not in self.tagcache:
            self.tagcache["Imported from old Datavault"] = self.fs.create_tag("Imported from old Datavault")
        self.tagcache["olddatavault"] = self.tagcache["Imported from old Datavault"]
        self.threadpool = []
        self.taglock = threading.Lock()
        self.local_imports = 0
        self.skipped_imports = 0
        self.downloaded_imports = 0

    def scrape(self):
        print "=" * 50
        print " Old ElasticSearch database importer starting..."
        print "=" * 50
        self.start_time = datetime.now()
        self.runtime = datetime.now() - self.start_time
        count = 50
        offset = 0
        if os.path.isfile("old_elasticsearch.status"):
            offset = json.loads(open("old_elasticsearch.status").read())["offset"]
        total = 0
        delay = 2

        print "Starting at %d, doing %d per run" % (offset, count)

        while True:
            query = {"query": {"match_all": {}}, "from": offset, "size": count}
            try:
                res = self.old_es.search(index=OLD_ES_INDEX, body=query)
            except elasticsearch.exceptions.ConnectionTimeout:
                print "\nTimeout on connection. Cooling off for %d seconds." % delay
                sys.stdout.flush()
                time.sleep(delay)
                continue

            total = res["hits"]["total"]

            perc = 100 * float(offset) / float(total)
            print "\r",
            print " "*100,
            print "\r[%s] Parsing %d-%d of %d (%d%%) [%dL %dD %dS]" % (self.runtime, offset, offset+count, total, perc, self.local_imports, self.downloaded_imports, self.skipped_imports),
            sys.stdout.flush()
            self.parse_hits(res["hits"]["hits"])
            offset += count
            f = open("old_elasticsearch.status", "w")
            f.write(json.dumps({"offset": offset}))
            f.close()
            if offset > total:
                break
            self.runtime = datetime.now() - self.start_time

        print "=" * 50
        print " Old ElasticSearch database importer done."
        print "=" * 50

    def parse_hits(self, hits):
        for hit in hits:
            t = threading.Thread(target=self.parse_hit, args=(hit,))
            t.daemon = True
            t.start()
            self.threadpool.append(t)

        if len(self.threadpool) > 50:
            # We never want more than 50 threads running at a time.
            for t in self.threadpool:
                t.join()

        self.threadpool = []


    def parse_hit(self, hit):
        f = File(self.fs)

        f._create_metadata()
        for key in FILE_METADATA_V1.keys():
            nkey = key
            if key == "metadata":
                nkey = "extra"

            f.meta[nkey] = hit["_source"][key]

        f.meta["is_resident"] = True
        f.meta["is_indexed"] = True
        f.meta["filename"] = f.meta["url"].split("/")[-1]
        f.meta["public_read"] = True
        f.meta["allowed_users"] = []
        f.meta["allowed_write_users"] = []
        f.meta["extra"]["oldid"] = hit["_id"]

        # Handle tags separately
        tags = f.meta["tags"]
        f.meta["tags"] = [self.tagcache["olddatavault"].id]
        self.taglock.acquire()
        try:
            for tag in tags:
                if tag in self.tagcache.keys():
                    f.meta["tags"].append(self.tagcache[tag].id)
                else:
                    self.tagcache[tag] = self.fs.create_tag(tag)
                    f.meta["tags"].append(self.tagcache[tag].id)
                    print "Created new tag: '%s'" % tag
        finally:
            self.taglock.release()

        # Pull in the actual file
        # (Here we can use a trick: We are copying this internally, 
        #   so rather than download it, let's just copy it from the
        #   actual source on the disk.
        #
        done = False
        if OLD_DATA_ROOT:
            old_path = urllib2.unquote(f.meta["url"].split("http://datatracker.org/data/")[1])
            old_path = os.path.join(OLD_DATA_ROOT, old_path)

            if os.path.isfile(old_path):
                fh = open(old_path)
                f.meta["hash"] = sha256sum(fh)
                fh.close()
                if not os.path.isfile(f.resident_location()):
                    shutil.copy(old_path, f.resident_location())
                    self.local_imports += 1
                else:
                    self.skipped_imports += 1
                done = True

        if not OLD_DATA_ROOT or not done:
            # Fallback: If we failed to get the file through normal means..
            fh = urllib2.urlopen(f.meta["url"])
            sio = StringIO.StringIO()
            sio.write(fh.read())
            fh.close()
            sio.seek(0)
            f.meta["hash"] = sha256sum(sio)
            if not os.path.isfile(f.resident_location()):
                wt = open(f.resident_location(), "w+")
                wt.write(sio.read())
                wt.close()
                self.downloaded_imports += 1
            else:
                self.skipped_imports += 1

        f._create_index()


if __name__ == "__main__":
    oesi = OldESImporter()
    oesi.scrape()
