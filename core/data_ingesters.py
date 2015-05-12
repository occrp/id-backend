import sys
from datetime import datetime
import csv 
from cassandra.cluster import Cluster
from cassandra import InvalidRequest
from optparse import OptionParser

class ParameterError(ValueError):
    pass

class Outputter:
    def error(self, msg):
        print "ERROR: %s" % msg
        raise Exception(msg)

class VerboseOutputter(Outputter):
    def mark(self):
        print "--------------------[ MARK ]---------------------"

    def notify(self, msg):
        print "[%s] %s" % (datetime.now(), msg)

class StreamOutputter(Outputter):
    def mark(self):
        print ""

    def notify(self, msg):
        print "\r%s" % (msg),
        sys.stdout.flush()

class SilentOutputter(Outputter):
    def mark(self):
        pass

    def notify(self, msg):
        pass

class Ingest:
    def __str__(self):
        return "%s" % (self.NAME)

class IngestCassandra(Ingest):
    NAME = "Cassandra"

    def __init__(self, options=None, outputter=SilentOutputter):
        if not options.cassandra_keyspace:
            raise ParameterError("Keyspace must be defined for Cassandra.")
        if not options.hosts:
            raise ParameterError("You must specify at least one host.")

        self.cluster = Cluster(options.hosts)
        self.outputter = outputter
        self.keyspace = options.cassandra_keyspace
        try:
            self.session = self.cluster.connect(self.keyspace)
        except InvalidRequest, e:
            self.outputter.error(e)

    def __str__(self):
        return "%s:%s" % (self.NAME, self.keyspace)

    def insert(self, table, fields):
        if not table:
            self.outputter.error("Must specify table.")
        try:
            self.session.execute("INSERT INTO %s (%s) VALUES (%s)" % (
                                 table, 
                                 ",".join(fields.keys()), 
                                 ",".join(["%s" for x in fields.values()])), 
                                 fields.values())
        except InvalidRequest, e:
            self.outputter.error(e)


    def ingest_csv(self, table, dictreader):
        cnt = 0
        starttime = datetime.now()
        lasttime = starttime
        for row in dictreader:
            self.insert(table, row)
            cnt += 1
            if cnt % 1000 == 0:
                curtime = datetime.now()
                lap = curtime - lasttime
                offset = curtime - starttime
                lasttime = curtime
                self.outputter.notify("cnt = %d (%s total; %s per set)" % (cnt, offset, lap))

class IngestApp:
    INGESTERS = {
        "cassandra": IngestCassandra
    }

    OUTPUTTERS = {
        "silent":   SilentOutputter,
        "stream":   StreamOutputter,
        "verbose":  VerboseOutputter,
    }

    def run(self):
        parser = OptionParser()
        parser.add_option("-f", "--file", action="append", dest="files", help="Ingest file", default=[])
        parser.add_option("-t", "--table", dest="table", help="Destination table")
        parser.add_option("-k", "--keyspace", dest="cassandra_keyspace", help="Keyspace (used with Cassandra ingester)")
        parser.add_option("-H", "--host", action="append", dest="hosts", default=[], help="Hosts. Specify multiple times for host pool.")
        parser.add_option("-d", "--directory", action="append", dest="directories",
                         help="Ingest directory", metavar="DIR", default=[])
        parser.add_option("-i", "--ingester", dest="ingester", default="cassandra",
                         help="Ingest to which database? (%s)" % (",".join(self.INGESTERS.keys())))
        parser.add_option("-O", "--outputter", dest="outputter", default="silent",
                         help="How verbose should we be? (%s)" % (",".join(self.OUTPUTTERS.keys())))

        (self.options, self.args) = parser.parse_args()

        if not self.options.outputter in self.OUTPUTTERS:
            print "Error: Unknown verbosity level '%s'. Try one of: %s." % (self.options.ingester, ",".join(self.INGESTERS.keys()))
            sys.exit(-1)

        if not self.options.ingester in self.INGESTERS:
            print "Error: Unknown ingester '%s'. Try one of: %s." % (self.options.ingester, ",".join(self.INGESTERS.keys()))
            sys.exit(-2)

        if self.options.files and self.options.directories:
            print "Can specify files or directories, but not both."

        outputter = self.OUTPUTTERS[self.options.outputter]()
        try:
            ingester = self.INGESTERS[self.options.ingester](options=self.options, outputter=outputter)
        except ParameterError, e:
            outputter.error("%s (from %s)" % (e, self.options.ingester))

        for f in self.options.files:
            outputter.notify("Ingesting %s into %s:%s" % (f, ingester, self.options.table))
            with open(f, "r") as fh:
                dr = csv.DictReader(fh)
                ingester.ingest_csv(self.options.table, dr)

        for d in self.options.directories:
            raise NotImplemented("Directory handling incomplete.")


if __name__ == "__main__":
    a = IngestApp()
    a.run()
