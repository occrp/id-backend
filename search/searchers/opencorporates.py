import urllib2
import urllib
import json

from search.searchers.base import DocumentSearcher, ResultSet
from search.searchers.base import DocumentSearchResult


def reconcile_matches(corp):
    url = 'http://opencorporates.com/reconcile?query=%s' % (
        urllib.quote(corp))
    data = json.load(urllib2.urlopen(url))
    return(data['result'])


def details_for_corp(corpid):
    url = 'http://api.opencorporates.com/%s' % corpid
    data = json.load(urllib2.urlopen(url))
    if 'results' not in data or 'company' not in data['results']:
        return None
    return data['results']['company']


class EntitySearchOpenCorporates(DocumentSearcher):
    PROVIDER = "OpenCorporates"

    def search(self, q, offset=0, limit=100, **kwargs):
        matches = reconcile_matches(q)
        resultset = ResultSet(total=len(matches))
        for match in matches[offset:offset+limit]:
            company = details_for_corp(match['id'])
            if company is None:
                continue
            result = DocumentSearchResult(self.PROVIDER,
                                          company.get('opencorporates_url'),
                                          company.get('updated_at'),
                                          company.get('company_type'),
                                          company.get('name'),
                                          metadata=company)
            resultset.append(result)
        return resultset
