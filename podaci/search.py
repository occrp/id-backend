import random
import logging
import pyes

from settings.settings import PODACI_ES_SERVERS, PODACI_ES_INDEX
from podaci.extract import get_file_text

log = logging.getLogger(__name__)

FILE = "podaci_file"
MAPPING = {
    FILE: {
        "properties": {
            "id": {"type": "long", "index" : "not_analyzed"},
            "url": {"type": "string", "index" : "not_analyzed"},
            "filename": {"type": "string"},
            "title": {"type": "string"},
            "text": {"type": u"string", "index": "analyzed"},
            "extracted_entities": {"type": "string"},
            "date_added": {"type": "date"},
            "tags": {"type": "string"},
            "schema_version": {"type": "float"},
            "allowed_users": {"type": "string"},
            "allowed_groups": {"type": "string"}
         }
    }
}


def connect():
    """ Connect to one of the specified ElasticSearch servers. """
    if PODACI_ES_SERVERS is None or not len(PODACI_ES_SERVERS):
        log.warn("PODACI_ES_SERVERS is not configured. No Podaci indexing.")
        return None
    return pyes.ES(PODACI_ES_SERVERS)

def ensure_index():
    """ Create the index and apply the mapping. """
    conn = connect()
    log.info("Creating index and mappings...")
    if conn is not None:
        conn.ensure_index(PODACI_ES_INDEX, mappings=MAPPING)

def index_file(file):
    """ Index a single PodaciFile object. """
    conn = connect()
    if conn is None:
        return
    data = file.to_json()
    data['text'] = get_file_text(file)
    conn.index(data, PODACI_ES_INDEX, FILE, id=file.id)

def search_files(query):
    pass
