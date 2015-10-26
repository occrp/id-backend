import logging
import pyes

from search.searchers.base import DocumentSearcher, ResultSet
from search.searchers.base import DocumentSearchResult

log = logging.getLogger(__name__)

# FIXME: What would life be without hard-coded server IPs?
DATATRACKER_HOST = '54.227.243.186:9200'
DATATRACKER_INDEX = 'id_prod'


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
            client = pyes.ES(DATATRACKER_HOST)
            results = client.search_raw(query, indices=[DATATRACKER_INDEX])
        except pyes.exceptions.ElasticSearchException as ese:
            log.error("Failure in DataTracker search: %r", ese)
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
