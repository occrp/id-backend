# csv2json.py
# 
# Copyright 2009 Brian Gershon -- briang at webcollective.coop
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import getopt
import csv
from os.path import dirname
import simplejson


def convert(in_file, out_file, model_name):
    print "Converting %s from CSV to JSON as %s" % (in_file, out_file)

    f = open(in_file, 'r' )
    fo = open(out_file, 'w')

    reader = csv.reader( f )

    header_row = []
    entries = []
    cnt = 0

    for row in reader:
        if not header_row:
            header_row = row
            continue

        cnt += 1
        pk = cnt
        model = model_name
        fields = {}
        for i in range(len(row)):
            active_field = row[i]
            if header_row[i] == "country_name":
                continue
            # convert numeric strings into actual numbers by converting to either int or float
            if active_field.isdigit():
                try:
                    new_number = int(active_field)
                except ValueError:
                    new_number = float(active_field)
                fields[header_row[i]] = new_number
            else:
                fields[header_row[i]] = active_field.strip()
            
        row_dict = {}
        row_dict["pk"] = int(pk)
        row_dict["model"] = model_name
        
        row_dict["fields"] = fields
        entries.append(row_dict)
	print "\rDone: %d" % cnt,
	sys.stdout.flush()

    print "\rConverted %d." % cnt
    fo.write("%s" % simplejson.dumps(entries, indent=4))

    f.close()
    fo.close()


if __name__ == "__main__":
    try:
        script, input_file_name, model_name = sys.argv
    except ValueError:
        print "\nRun via:\n\n%s input_file_name model_name" % sys.argv[0]
        print "\ne.g. %s airport.csv app_airport.Airport" % sys.argv[0]
        print "\nNote: input_file_name should be a path relative to where this script is."
        sys.exit()

    in_file = input_file_name
    out_file = input_file_name[:-4] + ".json"
    print "In file: %s; out file: %s" % (in_file, out_file)
    convert(in_file, out_file, model_name)
