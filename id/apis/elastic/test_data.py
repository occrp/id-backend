import datetime
import base64
from elastic import SCHEMA_VERSION

sample_docs = [
{ # an almost-blank document
        'url': '',
        'title': '',
        'text': 'blah blah blah',
        'extracted_entities': [],
        'date_added': datetime.datetime.now(),
        'allowed_users': ['ohuiginn@gmail.com'],
        'allowed_groups': ['groups_all_id'],
        'tags': ['test1', 'test4'],
        'schema_version': SCHEMA_VERSION,
        },
{ # a document with some text
        'url': 'https://docs.google.com/a/occrp.org/file/d/0BynfMoj8NYD3OUNKZjFjWHZ0bVU/edit',
        'title': 'record_524911.html',
        'text': '''

Here is some text about Panama to search

        ''',
        'extracted_entities': ['Mompracem International S.A.'],
        'date_added': datetime.datetime.now(),
        'allowed_groups': ['not_visible_to_any_group'],
        'allowed_users': ['ohuiginn@gmail.com'],
        'tags': ['test1', 'test2'],
        'schema_version': SCHEMA_VERSION,
    },
{ # a document with a file included
# XXX needs a fixup
        'url': 'https://docs.google.com/a/occrp.org/file/d/0BynfMoj8NYD3OUNKZjFjWHZ0bVU/edit',
        'title': 'record_524911.html',
        'text': '''
        This text is supplementary to that contained by the document
        ''',
#'file': base64.b64encode(open('sampledoc.pdf').read()),
        'date_added': datetime.datetime.now(),
        'allowed_groups': ['groups_staff_id'],
        'tags': ['test2', 'test4'],
        'schema_version': SCHEMA_VERSION,
    },
        ]


expected_metadata_sampledoc = {
    # tika metadata extraction on sampledoc.pdf
    # nb this may need updates following tika upgrades or config changes

    u'Author': u'sgonzalez',
    u'Content-Type': u'application/pdf',
    u'Creation-Date': u'2013-01-09T15:52:38Z',
    u'Last-Modified': u'2013-01-09T15:52:38Z',
    u'Last-Save-Date': u'2013-01-09T15:52:38Z',
    u'created': u'Wed Jan 09 15:52:38 UTC 2013',
    u'creator': u'sgonzalez',
    u'date': u'2013-01-09T15:52:38Z',
    u'dc:creator': u'sgonzalez',
    u'dc:title': u'Visual FoxPro',
    u'dcterms:created': u'2013-01-09T15:52:38Z',
    u'dcterms:modified': u'2013-01-09T15:52:38Z',
    u'meta:author': u'sgonzalez',
    u'meta:creation-date': u'2013-01-09T15:52:38Z',
    u'meta:save-date': u'2013-01-09T15:52:38Z',
    u'modified': u'2013-01-09T15:52:38Z',
    u'producer': u'Bullzip PDF Printer / www.bullzip.com / Freeware Edition',
    u'title': u'Visual FoxPro',
    u'xmpTPg:NPages': 1
}
