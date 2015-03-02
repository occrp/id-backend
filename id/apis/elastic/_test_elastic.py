

import unittest
from test_data import *
from importtools.walklisting import iterate_apache_dir
from importtools.importutils import luxembourg_date
import elastic
import time
import datetime
import dateutil.parser
import os
import uuid

# any tests creating fixtures on ES should create indexes starting like this
INDEX_PREFIX = 'id_test'

def test_directory_listing():
    dirurl = 'http://www.eurograds.com/maps/'
    fileurls = set(iterate_apache_dir(dirurl))
    assert 'http://www.eurograds.com/maps/bosnia_herzegovina.gif' in fileurls
    assert 'http://www.eurograds.com/' not in fileurls

def test_lux_extract_title():
    filepath = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'importtools/luxembourg_text.txt')
    filetext = open(filepath).read()
    assert luxembourg_date(filetext) == "3 Janvier 2008"

def test_esearch_connect():
    # more checking the server status than the code
    cs = elastic.esconn().cluster_state()
    assert isinstance(cs, dict)


def test_upload_from_url():
    # XXX relies on setup from test_install_mapping
    sampledoc = 'http://datatracker.org/data/SWISS%202008/009-15012008-1.pdf'
    elastic.upload_from_url(sampledoc)
    time.sleep(1)

    
class ESTest(unittest.TestCase):
    # random element in index is to prevent simultaneously-run
    # tests interfering with one another
    index = 'id_test_%s' % uuid.uuid4().hex[:6]

    def setUp(self):
        elastic.wipe_index(self.index)
        elastic.install_index(index=self.index,
                              schema=elastic.es_schema,
                              doctype='datavault_doc')
        for doc in sample_docs:
            elastic.esconn().index(doc, self.index, 'datavault_doc')
        # give ES a moment to update the index
        time.sleep(2)

    def tearDown(self):
        elastic.wipe_index(self.index)

    def test_basic_search(self):
        assert elastic.search_raw('Panama', index=self.index)['hits']['total'] == 1

    def test_standard_fields(self):
        for doc in elastic.show_all_docs(index=self.index):
            assert doc['_source']['schema_version'] == elastic.SCHEMA_VERSION

        # time check must be loose, because time in the fixtures is
        # set at import time
            assert (
                dateutil.parser.parse(doc['_source']['date_added']) -
                datetime.datetime.now()).total_seconds() < 1000

    def test_acl(self):
        pass #XXX write me!

class TestDriveUploads(unittest.TestCase):
    documents = [
        'https://docs.google.com/spreadsheet/ccc?key=0AqUALHBes1lRdGp0bGdCVzViZ2JHOVdIREQ3cDlBQmc&usp=sharing']

    def test_extract_content(self):
        pass

class TestTika(unittest.TestCase):

    def setUp(self):
        docfn = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'sampledoc.pdf')
        self.sampledoc = open(docfn).read()

    def test_tika_text(self):
        result = elastic.tika_get_text(self.sampledoc)
        assert 'SMART INVEST GROUP' in result

    def test_tika_metadata(self):
        result = elastic.tika_get_metadata(self.sampledoc)
        assert (
            sorted(result.items()) ==
            sorted(expected_metadata_sampledoc.items())
            )

