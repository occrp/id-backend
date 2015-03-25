import csv
import sys

csv.field_size_limit(sys.maxsize)

# See http://download.geonames.org/export/dump/ for details:
places_fieldnames = ('geonameid', 'name', 'asciiname', 'alternatenames', 'latitude', 
                     'longitude', 'featureclass', 'featurecode', 'countrycode',
                     'cc2', 'admin1code', 'admin2code', 'admin3code', 'admin4code', 
                     'population', 'elevation', 'dem', 'timezone', 'modification_date', 'source')

countries_fieldnames = ('iso', 'iso3', 'isonumeric', 'fips', 'country', 'capital', 
                        'area', 'population', 'continent', 'tld', 'currencycode',
                        'currencyname', 'phone', 'postal_code_format', 'postal_code_regex',
                        'languages', 'geonameid', 'neighbours', 'equivalentfipscode', 'source')

featureclasses = {
    'A': 'regions.csv',
    'H': 'waterbodies.csv',
    'L': 'areas.csv',
    'P': 'places.csv',
    'R': 'roads.csv',
    'S': 'locations.csv',
    'T': 'elevation.csv',
    'U': 'undersea.csv',
    'V': 'vegetation.csv'
}

def try_cast(l):
    r = []
    for x in l:
        try: x = float(x)
        except: pass
        try: x = int(x)
        except: pass
        r.append(x)
    return r

def get_country(iso):
    global countries
    graph = Graph()
    country = countries.get(iso, None)
    if not country:
        countries[iso] = graph.find_one("Country", iso=iso)
    if not country:
        countries[iso] = graph.create("Country", iso=iso)[0]
    return countries[iso]

def clean_countries():
    # TODO: Split currencies out as separate entities
    print "Cleaning countries...",
    sys.stdout.flush()
    fp = open('countryInfo.txt', 'r')
    countries_tsv = csv.reader((row for row in fp if not row.startswith('#')), dialect='excel-tab')
    output = csv.writer(open('output/countries.csv', 'w'))
    output.writerow(countries_fieldnames)
    for country in countries_tsv:
        country.append("GeoNames")
        output.writerow(country)

    print "DONE (%d)" % countries_tsv.line_num


def split_places():
    print "Splitting places...",
    sys.stdout.flush()

    places_tsv = csv.reader(open('allCountries.txt', 'r'), delimiter='\t', quoting=csv.QUOTE_NONE)
    outputs = {}

    for featureclass in featureclasses.keys():
        outputs[featureclass] = csv.writer(open("output/%s" % featureclasses[featureclass], "w"))
        outputs[featureclass].writerow(places_fieldnames)

    altnames = csv.writer(open("output/altnames.csv", "w"))
    altnames.writerow(["geonameid", "name"])

    try:
        for place in places_tsv:
            place.append("GeoNames")
            data = dict(zip(places_fieldnames, place))
            for altname in data["alternatenames"].split(","):
                altnames.writerow([data["geonameid"], altname])
            try:
                outputs[data["featureclass"]].writerow(place)
            except Exception, e:
                print "Error %s on %s" % (e, data)

            # Show some status every now and then:
            if places_tsv.line_num % 100 == 0:
                print "\rSplitting places... %d" % (places_tsv.line_num),
                sys.stdout.flush()
    except Exception, e:
        print "CSV ERROR: ", e


    print "DONE"

if __name__ == "__main__":
    clean_countries()
    split_places()
