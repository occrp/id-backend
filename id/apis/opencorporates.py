import urllib2
import urllib
import json

import metasearch

OCVERSION = 'v0.2'

def reconcile_matches(corp):
    url = 'http://opencorporates.com/reconcile?query=%s' % (
        urllib.quote(corp))
    data = json.load(urllib2.urlopen(url))
    return(data['result'])

def details_for_corp(corpid):
    url = 'http://api.opencorporates.com/%s%s' % (OCVERSION, corpid)
    data = json.load(urllib2.urlopen(url))
    return data['results']

def corp_keydata(fulldata):
    if 'company' in fulldata: #hack hack hack
        fulldata = fulldata['company']
    kd = {
      'country' : fulldata.get('jurisdiction_code', ''),
      'name' : fulldata.get('name', '').title(),
      'source': (fulldata.get('source', {}) or {}).get('url', ''),
      'officers': [x['officer'].get('name', '').title() for x in fulldata.get('officers', [])],
      'address': fulldata.get('registered_address_in_full', u'') or u'',
      'url': fulldata['opencorporates_url'],
            }
    return(kd)


class OpenCorpSearch(metasearch.MetaSearchProvider):
    # take a query, make a metasearch
    def search(self, query, offset=0, limit=10):
        matches = reconcile_matches(query)
        results = []
        for match in matches[offset:offset+limit]:
            corp = match['id']
            details = details_for_corp(corp)
            keydata = corp_keydata(details)
            results.append(keydata)
        return metasearch.SearchResult(
            query, results, resultcount=len(matches))


class OpenCorpBulkSearch(metasearch.MetaSearchBulkProvider):
    providername = 'OpenCorporates'
    providerclass = OpenCorpSearch


class MontenegroSWSearch(metasearch.ScraperWiki):
    pass

class MontenegroSWBulkSearch(metasearch.ScraperWikiBulk):
    providername = 'Montenegro Company Records (scraperwiki'
    providerclass = MontenegroSWSearch
