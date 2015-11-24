import logging
import pyes

from django.conf import settings
from search.searchers.base import DocumentSearcher, ResultSet
from search.searchers.base import DocumentSearchResult

log = logging.getLogger(__name__)


class DocumentSearchDataTracker(DocumentSearcher):
    PROVIDER = "DataTracker"

    def search(self, q, offset=0, limit=100, **kwargs):
        query = {
            'query': {
                'query_string': {
                    'query': q,
                    'default_operator': 'AND',
                }
            },
            'from': offset,
            'size': limit,
            'fields': ['url', 'title', 'date_added', 'tags'],
            'highlight': {
                'fields': {
                    'text': {}
                }
            }
        }
        try:
            client = pyes.ES(settings.DATATRACKER_ES_SERVERS)
            results = client.search_raw(query, indices=[settings.DATATRACKER_ES_INDEX])
        except Exception as ex:
            log.info("Failure in DataTracker search: %r", ex)
            return ResultSet(total=0)

        resultset = ResultSet(total=results['hits']['total'])
        for r in results['hits']['hits']:
            text = r.get('highlight', {}).get('text', [])
            text = '<br/>'.join(text)
            field = lambda n: r["fields"].get(n, '')
            i = DocumentSearchResult(self.PROVIDER, field('url'),
                                     field('date_added'),
                                     text, field('title'),
                                     metadata=r)
            resultset.append(i)
        return resultset
