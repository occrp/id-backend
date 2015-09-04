import requests
import logging
from django.conf import settings

from search.searchers.base import DocumentSearcher, ResultSet
from search.searchers.base import DocumentSearchResult

log = logging.getLogger(__name__)

SEARCH_URL = 'https://api.opencorporates.com/v0.4/companies/search'


class EntitySearchOpenCorporates(DocumentSearcher):
    PROVIDER = "OpenCorporates"

    def search(self, q, offset=0, limit=20, **kwargs):
        if settings.OPENCORPORATES_API_TOKEN is None:
            log.debug("No API token for OpenCorporates, failing.")
            return ResultSet(total=0)

        log.debug("Searching OpenCorporates for: %r", q)
        try:
            if q is None or not len(q.strip()):
                raise ValueError('No query')
            res = requests.get(SEARCH_URL, params={
                'q': q,
                'api_token': settings.OPENCORPORATES_API_TOKEN,
                'per_page': limit,
                'page': int(1 + offset / max(1, limit))
            })
            results = res.json()
            if 'error' in results:
                raise ValueError(results.get('error'))
            results = results.get('results', {})
        except Exception as e:
            log.exception(e)
            return ResultSet(total=0)

        resultset = ResultSet(total=results.get('total_count'))
        for match in results.get('companies', []):
            company = match.get('company')
            result = DocumentSearchResult(self.PROVIDER,
                                          company.get('opencorporates_url'),
                                          company.get('updated_at'),
                                          company.get('company_type'),
                                          company.get('name'),
                                          metadata=company)
            resultset.append(result)
        return resultset
