# coding: utf-8
'''
Setup for the elastic search system
This needs to be deployed to an elasticsearch server

XXX: some of this should eventually be moved to the general config server
'''

import pyes
import logging
import pprint
import traceback
import datetime
import base64
import urllib2
import socket
import subprocess
import json
import requests
import random
import re
import pprint
import importutils
from collections import defaultdict

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('elasticsearch')

ES_HOSTS = [
            'http://54.227.243.186:9200'
           ]

TIKA_HOSTS = [
              '54.227.243.186/',
              ]
TIKA_PORT_CONTENT = 8010
TIKA_PORT_METADATA = 8011
ES_AUTH = {
    'username': 'occrp',
   'password': 'X6fRfCsUuv2g7mj4gfUv'
    }
INDEX = 'id_test'
SCHEMA_VERSION = 1

# there is a Tika plugin for elasticsearch. Reasons for not using it are:
#  - it is not very flexible
#  - when using it, we cannot also do opencalais entity extraction
#  - while breaking out tika introduces a separate round trip, it gives us
#    much greater ability to break things out into other servers

TIKA_SERVER = '174.129.138.69:8005'

#conns = [pyes.ES(x, basic_auth = ES_AUTH) for x in ES_HOSTS]
conns = [pyes.ES(x) for x in ES_HOSTS]
def esconn():
    return random.choice(conns)

es_schema = { "document": { "properties": {
    "url": {"type": "string",
            "index" : "not_analyzed"},
    "title": {"type": "string"},
    "text": {"type": u"string",
             'index': 'analyzed',
                        },

    "extracted_entities": {"type": "string"},
    "date_added": {"type": "date"},
    "tags": {"type": "string"},
    # ideally we would get the code version from git, and turn it into some
    # numeric form. For now, we'll have something taken from a config var
    "schema_version": {"type": "float"},
    "allowed_users": {"type": "string"}, # XXX should be indexed for abs match
    "allowed_groups": {"type": "string"},
     } # close properties
     } # close document
     } # close schema


def wipe_index(indexname, force=False):
    if indexname in ('id_dev', 'id_prod') and not force:
        print("Aborting. If you REALLY want to delete %s, call with force=True")
        return
    try:
        esconn().delete_index(indexname)
        log.info('deleted info')
    except Exception: #if the index doesn't exist
        log.info('unable to delete index; it likely does not exist')

def install_index(index, schema=es_schema, doctype='datavault_doc'):
    conn = esconn()
    conn.create_index(index)
    conn.put_mapping(doctype, schema['document'], [index])

def test_connection():
    # get cluster state as an example
    cs = esconn().cluster_state()
    return isinstance(cs, dict)


def show_all_docs(index):
    # return all docs in an index
    # will raise KeyError if the index does not exist
    query = {
            "query": {"match_all": {}},
            }
    results = runquery(query, index)
    return results['hits']['hits']


def runquery(query, index):
    # ideally here we would use
    #    return conn.search_raw(query)
    # but that somehow plays badly with GAE, so let's build our own request

    url = '%s/%s/_search' % (random.choice(ES_HOSTS), index)
    result = requests.post(
        url,
        json.dumps(query),
        #auth=requests.auth.HTTPBasicAuth(ES_AUTH['username'], ES_AUTH['password'])
        )
    return json.loads(result.text)


def search_raw(
        term, allowed_users=[], allowed_groups=['groups_all_id'],
        limit=10, offset=0, index=INDEX):
    query = build_search_query(term, offset, limit, allowed_users, allowed_groups)
    return runquery(query, index)

def build_search_query(term, offset, limit, allowed_users, allowed_groups):
    # building our own query gives us more power than pyes
    query = {
        'query': {
            'query_string': {
                'query': term,
                'default_operator': 'AND',
                     }
                },
        'from': offset,
        'size': limit,
        'fields': [
            'url', 'title', 'tags', 'date_added',
            'allowed_users', 'allowed_groups'
            ],
        'highlight': {
            'fields' : {
                'url' : {},
                'title': {},
                'tags': {},
                'text': {}
                }
             },
        "filter": {"or": [
            {'terms': {
                'allowed_groups': [allowed_groups]}
                },
            {'terms': {
                'allowed_users': [allowed_users]}
                }
            ]
            }

            }
    return query

def search(*args, **kwargs):
    results = search_raw(*args, **kwargs)

    #XXX dirty fix for messy data (repeated tags)
    for r in results['hits']['hits']:
        r['fields']['tags'] = sorted(set(r['fields']['tags']))
    return results

class UrlUploader(object):
    doctype = 'datavault_doc'
    tags = []

    def __init__(self,
                 url,
                 title='',
                 tags=[],
                 allowed_groups = ("groups_all_id"),
                 allowed_users = (),
                 index=INDEX):
        self.url = url
        self.title = title
        self.tags = tags + self.tags
        self.index = index
        self.allowed_groups = allowed_groups
        self.allowed_users = allowed_users

    def check_existing(self):
        '''return True if an item with this URL exists in the index
        If it does, we should usually either abort, or update the
        existing document'''
        result = esconn().count(query = {'match': {'url': self.url}}, indices=[self.index])
        return result['count'] > 0

    def get_contents(self):
        self.contents = urllib2.urlopen(self.url).read()

    def tika(self):
        self.text = tika_get_text(self.contents)
        self.metadata = tika_get_metadata(self.contents)

    def get_title(self):
        self.title = (self.title
             or self.metadata.get('title', None)
             or self.metadata.get('dc:title', None)
             or url.split('/')[-1].rsplit('.', 1)[0]
             )

    def doc_modifications(self, doc):
        '''Use this to make any subclass-specific changes to the document'''
        return doc

    def upload(self):
        doc = {
            'date_added': datetime.datetime.now(),
            'schema_version': SCHEMA_VERSION,
            'url': self.url,
            'title': self.title,
            'tags': self.tags or [],
            'text': self.text,
            'metadata': self.metadata,
            'allowed_users': self.allowed_users,
            'allowed_groups': self.allowed_groups
            }
        doc = self.doc_modifications(doc)
        esconn().index(doc, self.index, self.doctype)
        doc.pop('text')


    def run(self):
        if self.check_existing():
            log.info('url already in db: %s' % self.url)
            return
        self.get_contents()
        self.tika()
        self.get_title()
        self.upload()

class GoogleUrlUploader(UrlUploader):

    tags = ['Google Drive']

    def get_contents(self):
        pass

class LuxembourgGazette(UrlUploader):
    tags = ['Gazette', 'Luxembourg']

    def get_title(self):
        from_md = self.metadata.get('dc:title', None)
        if from_md:
            self.title = "Luxembourg Gazette %s" % from_md
        else:
            gazdate = importutils.luxembourg_date(self.text)
            if gazdate:
                self.title = "Luxembourg Gazette, %s" % gazdate
            else:
                self.title = "Luxembourg Gazette"

class SwissGazette(UrlUploader):
    tags = ['Gazette', 'Switzerland']

    def get_title(self):
        self.title = 'Swiss Gazette'

class PanamaCompany(UrlUploader):
    tags = ['Panama', 'Company Register']

    def get_title(self):
        match = re.search('Nombre de la Sociedad\W+([^\n\t]+)\n', self.text, re.MULTILINE)
        if match:
            self.title = '%s (Panama Company)' % match.group(1)
        else:
            self.title = 'Panama Company'



def upload_from_url(url, *args, **kwargs):
    '''
    call this function with appropriate args for UrlUploader.__init__
    It will initialize and run an appropriate UrlUploader subclass
    '''
    if 'docs.google.com' in url:
        uploader_class = GoogleUrlUploader
    elif 'data/LUXEMBOURG' in url:
        uploader_class = LuxembourgGazette
    elif 'data/SWISS' in url:
        uploader_class = SwissGazette
    elif 'data/panama' in url:
        uploader_class = PanamaCompany
    else:
        uploader_class = UrlUploader
    uploader = uploader_class(url, *args, **kwargs)
    uploader.run()

def send_to_port(hostname, port, content):
    '''
    for some reason this hangs if I use the python socketlib
    I'll fix it eventually, but for now i'm taking the easy way out
    XXX this means uploading will not work from GAE
    '''
    cmd = 'nc %s %s' % (hostname, port)
    nc = subprocess.Popen(
        cmd,
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    (stdout, stderr) = nc.communicate(content)
    return stdout


def tika_get_text(text):
    return send_to_port(random.choice(TIKA_HOSTS), TIKA_PORT_CONTENT, text)


def tika_get_metadata(text):
    astext = send_to_port(random.choice(TIKA_HOSTS), TIKA_PORT_METADATA, text)
    return json.loads(astext)

def clear_duplicates(term, index):
    matches = defaultdict(list)
    query = build_search_query(
        term=term, offset=0, limit=99999,
        allowed_users = (),
        allowed_groups = ('groups_all_id'),)
    results = runquery(query, index)
    for hit in results['hits']['hits']:
        matches[hit['fields']['url']].append(hit)
    to_destroy = []
    for url, items in matches.iteritems():
        for dupe in items[1:]:
            to_destroy.append(dupe['_id'])
    print('going to destroy %s items' % len(to_destroy))
    for dupe_id in to_destroy:
        conns[0].delete(index, 'datavault_doc', dupe_id)
        print('deleted %s' % dupe_id)
    return matches, to_destroy
