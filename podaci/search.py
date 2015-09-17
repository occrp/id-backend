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
            "sha256": {"type": "string", "index": "not_analyzed"},
            "url": {"type": "string", "index": "not_analyzed"},
            "mimetype": {"type": "string", "index": "not_analyzed"},
            "filename": {"type": "string"},
            "title": {"type": "string", "index": "analyzed", "store": True},
            "text": {"type": u"string", "index": "analyzed"},
            "date_added": {"type": "date"},
            "tags": {"type": "string"},
            "size": {"type": "long"},
            "staff_read": {"type": "boolean"},
            "public_read": {"type": "boolean"},
            "schema_version": {"type": "float"},
            # allowed_users_read
            "allowed_users": {"type": "integer"}
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


def ensure_index(clear=False):
    """ Create the index and apply the mapping. """
    conn = connect()
    log.info("Creating index and mappings...")
    if conn is not None:
        try:
            conn.ensure_index(settings.PODACI_ES_INDEX, mappings=MAPPING,
                              clear=clear)
        except pyes.exceptions.ElasticSearchException as ese:
            log.error("Failed to ensure the index exists. Is ElasticSearch " +
                      "running or do you need to regenerate the index?")


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

def authorize_filter(user):
    """ Generate a filter against files which expresses the user's access
    rights. """
    simple = {'term': {'public_read': True}}
    if user is None or user.is_anonymous():
        return simple
    preds = [simple, {'term': {'allowed_users_read': user.id}}]
    if user.is_staff:
        preds.append({'term': {'staff_read': True}})
    return {"or": preds}
