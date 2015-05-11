import csv
import sys
import os

class DirectoryAnalyzer:
    def __init__(self, verbose=False, max_scan=-1, table_prefix=""):
        self.analyzers = {}
        self.verbose = verbose
        self.max_scan = max_scan
        self.table_prefix = table_prefix

    def analyze(self, path):
        for fn in os.listdir(path):
            fullpath = os.path.join(path, fn)
            if self.verbose:
                print "Analyzing %s" % fullpath
            if fn.endswith(".csv"):
                a = CSVAnalyzer(self.verbose, self.max_scan)
                if a.analyze(fullpath):
                    self.analyzers[fullpath] = a
                else:
                    print "DirectoryAnalyzer: Could not correctly analyze CSV file '%s'" % fullpath
            else:
                print "DirectoryAnalyzer: Not sure what to do with '%s'" % fullpath

    def get_cassandra_tables(self):
        s = ""
        for path, analyzer in self.analyzers.iteritems():
            table = analyzer.make_cassandra_table(table_prefix=self.table_prefix)
            s += "\n-- Table for %s:\n%s\n" % (path, table)
        return s


class CSVAnalyzer:
    def __init__(self, verbose=False, max_scan=-1):
        self.verbose = verbose
        self.max_scan = max_scan
        self.fields = []
        self.types = {}
        self.filename = ""

    def analyze(self, filename):
        self.filename = filename
        with open(filename) as self.fh:
            if not self.detect_header():
                return False
            self.reader = csv.DictReader(self.fh)
            self.fields = self.reader.fieldnames
            self.types = self.get_datatypes()
        return True

    def detect_header(self):
        self.fh.seek(0)
        try:
            has_header = csv.Sniffer().has_header(self.fh.read(1024))
        except csv.Error, e:
            if self.verbose:
                print "CSVAnalyzer: %s" % e
            return False
        self.fh.seek(0)
        return has_header

    def get_datatype(self, value):
        try: 
            if int(value): return int
        except: pass
        try: 
            if float(value): return float
        except: pass
        return str

    def worse(self, a, b):
        # I think this works right...
        if a == int: return False
        if a == float and b == int: return False;
        if b == str: return True
        return False

    def get_datatypes(self):
        i = 0
        dt = {}
        for row in self.reader:
            i += 1
            ds = self.get_datatypes_for_line(row)
            if dt == {}:
                dt = ds
            else:
                for j in ds.keys():
                    if self.worse(ds[j], dt[j]):
                        dt[j] = ds[j]
            if self.max_scan >= 0 and i >= self.max_scan:
                break
            if self.verbose:
                if i % 1000 == 0:
                    print "\rChecking row %d for data types." % i,
                    sys.stdout.flush()
        if self.verbose:
            print ""
        return dt

    def get_datatypes_for_line(self, line):
        res = {}
        for key, value in line.iteritems():
            res[key] = self.get_datatype(value)
        return res

    def name_to_cassandra_name(self, name):
        return name.lower().replace(" ", "_").replace("-", "_").replace(",", "_")

    def type_to_cassandra_type(self, t):
        tlookup = {
            str:    "text",
            int:    "int",
            float:  "double",
        }
        return tlookup[t]

    def make_cassandra_table(self, tablename=None, aftermatter="", table_prefix=""):
        template = "CREATE TABLE IF NOT EXISTS %(table_prefix)s%(name)s (\n\t%(fields)s\n)%(aftermatter)s;"
        fields = []
        if not tablename:
            tablename = self.filename.split("/")[-1].strip(".csv")
        for name, t in self.types.iteritems():
            fields.append("%s: %s" % (self.name_to_cassandra_name(name), self.type_to_cassandra_type(t)))

        return template % {
                "table_prefix": table_prefix,
                "name": self.name_to_cassandra_name(tablename), 
                "fields": ",\n\t".join(fields),
                "aftermatter": aftermatter}

if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-d", "--directory", action="append", dest="directory",
                     help="Analyze directory", metavar="DIR", default=[])
    parser.add_option("", "--cassandra", action="store_true", dest="cassandra", default=False,
                     help="Print out Cassandra table specifications for found data.")
    parser.add_option("-M", "--max-scan", type="int", default=-1, dest="max_scan",
                     help="The maximum number of file entries that should be scanned to determine types.")
    parser.add_option("-q", "--quiet",
                     action="store_false", dest="verbose", default=True,
                     help="Don't print status messages to stdout")
    parser.add_option("", "--table-prefix", dest="table_prefix", default="", 
                     help="Add a prefix to all data structure names output.")

    (options, args) = parser.parse_args()

    # print options
    for d in options.directory:
        an = DirectoryAnalyzer(options.verbose, options.max_scan, options.table_prefix)
        an.analyze(d)
        if options.cassandra:
            print an.get_cassandra_tables()

