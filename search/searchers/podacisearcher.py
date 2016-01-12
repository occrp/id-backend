import logging
from django.core.urlresolvers import reverse

from podaci.search import search_files_raw, authorize_filter
from search.searchers.base import DocumentSearcher, ResultSet
from search.searchers.base import DocumentSearchResult

log = logging.getLogger(__name__)


class DocumentSearchPodaci(DocumentSearcher):
    PROVIDER = "ID Files"

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
            'fields': [
                'url', 'title', 'date_added', 'filename',
                'created_by', 'mimetype'
            ],
            'highlight': {
                'fields': {
                    'text': {}
                }
            }
        }
        user = self.request.requester if self.request else None
        query['filter'] = authorize_filter(user)
        try:
            results = search_files_raw(query)
        except Exception as ex:
            log.info("Failure in Podaci search: %r", ex)
            return ResultSet(total=0)

        if not results.has_key('hits'):
            return ResultSet(total=0)

        resultset = ResultSet(total=results['hits']['total'])
        for r in results['hits']['hits']:
            text = '<br/>'.join(r.get('highlight', {}).get('text', []))
            field = lambda n: ''.join(r["fields"].get(n, []))

            url = field('url')
            if url is None or not len(url):
                url = reverse('podaci_file_detail', kwargs={'pk': r['_id']})

            title = field('title')
            if title is None or not len(title):
                title = field('filename')

            i = DocumentSearchResult(self.PROVIDER, url, field('date_added'),
                                     text, title, metadata=r)
            resultset.append(i)
        return resultset
