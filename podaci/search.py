import logging
import pyes

from django.conf import settings
from podaci.extract import get_file_text

log = logging.getLogger(__name__)

FILE = "podaci_file"
MAPPING = {
    FILE: {
        "properties": {
            "id": {"type": "long", "index": "not_analyzed"},
            "url": {"type": "string", "index": "not_analyzed"},
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
    if settings.PODACI_ES_SERVERS is None or \
            not len(settings.PODACI_ES_SERVERS):
        log.warn("PODACI_ES_SERVERS is not configured. No Podaci indexing.")
        return None
    return pyes.ES(settings.PODACI_ES_SERVERS)


def ensure_index():
    """ Create the index and apply the mapping. """
    conn = connect()
    log.info("Creating index and mappings...")
    if conn is not None:
        conn.ensure_index(settings.PODACI_ES_INDEX, mappings=MAPPING)


def index_file(file):
    """ Index a single PodaciFile object. """
    conn = connect()
    if conn is None:
        return
    data = file.to_json()
    data['text'] = get_file_text(file)
    conn.index(data, settings.PODACI_ES_INDEX, FILE, id=file.id)


def search_files_raw(query):
    """ Run a search and return the ES index repr of the matching files. """
    conn = connect()
    if conn is None:
        return {}
    return conn.search_raw(query, indices=[settings.PODACI_ES_INDEX],
                           doc_types=[FILE])
