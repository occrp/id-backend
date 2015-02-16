
'''
Base classes for the metasearch system.
Subclass to implement a specific search engine
'''

import requests
import logging

class MetaSearchProvider:

    def search(self, query):
        raise NotImplementedError

class MetaSearchBulkProvider:

    providername = 'MetaSearch'
    providerclass = MetaSearchProvider
    headers = None

    def __init__(self, *args, **kwargs):
        self.provider = self.providerclass()

    def search(self, queries):
        resultlist = SearchResultList(self.providername,
                                      headers = self.headers)
        for query in queries:
            resultlist.add_result(self.provider.search(query))
        return resultlist

class ScraperWiki(MetaSearchProvider):
    baseurl = 'https://api.scraperwiki.com/api/1.0/datastore/sqlite'
    tablename = 'me_cmp_list'
    basedata = {
        'format': 'jsondict'}

    def generate_sql_query(self, searchterm):
        # XXX: need safe interpolation here
        query = "select * from swdata where company_name like '%" + searchterm + "%' limit 10;"
        logging.debug(query)
        return query

    def sr_from_json(self, query, jsdata):
        labelmap = {
            'url' : 'link',
            'name': 'company_name',
            'address': 'place',
            }
        for item in jsdata:
            for (k,v) in labelmap.items():
                item[k] = item[v]
                item['officers'] = []
                item['country'] = 'Montenegro' # XXX change this!
        return SearchResult(query, jsdata)

    def search(self, query):
        data = {
            'format' : 'jsondict',
            'name': self.tablename,
            'query': self.generate_sql_query(query)
            }
        req = requests.get(self.baseurl, params = data)
        sr = self.sr_from_json(query, req.json())
        return sr

def test_scraperwiki():
    sw = ScraperWiki()
    return sw.search('oliv')

class ScraperWikiBulk(MetaSearchBulkProvider):
    providername = 'ScraperWiki'
    providerclass = ScraperWiki

class SearchResult(object):
    # resultcount is a string rather than an integer
    # this allows for values like '>10'
    resultcount = u'Unknown'
    resultdata = []

    def __init__(self, querystring, resultdata, resultcount = None):
        if resultcount is None:
            resultcount = len(resultdata)
        self.resultcount = resultcount
        self.resultdata = resultdata
        self.querystring = querystring
        rawheaders = sorted(self.resultdata[0].keys()) if self.resultdata else []
        #remove hardcoded fields
        self.hard_headers = ['name']
        self.dynamic_headers = [x for x in rawheaders if x not in ('name', 'url')]
        self.headers = self.hard_headers + self.dynamic_headers

    def output_resultdata(self):
        '''
        We take 'name' and 'url' as a special case for the 1st column
        the rest goes in
        '''
        output = []
        for line in self.resultdata:
            output.append({
                'name': line.get('name', ''),
                'url': line.get('url', ''),
                'columns': [line.get(k, '') for k in self.dynamic_headers]
                })
        return output

    def flatdata(self):
        return {
            'querystring': self.querystring,
            'resultcount': self.resultcount,
            'resultdata' : self.resultdata,
            }

    def datadict(self):
        results = {
            'querystring': self.querystring,
            'resultcount': self.resultcount,
            'resultdata' : self.output_resultdata(),
            }
        return results


class CompanySearchResult(SearchResult):
    pass

class SearchResultList(object):
    '''Groups the search results from a single provider
    '''

    results = [] #iterable of CompanySearchResult
    provider = None #for now, a string to identify where this comes from

    def __init__(self, provider, results = None, headers = None):
        self.provider = provider
        self.results = results or []
        self._headers = headers

    def add_result(self, result):
        self.results.append(result)

    def headers(self):
        #grab headers from first search term that gives any data
        return self._headers or next((x.headers for x in self.results if x.headers), [])

    def as_tuples(self):
         return {
            'provider': self.provider or 'Unknown Provider',
            'headers': self.headers(),
            'data': [x.datadict() for x in self.results],
            }

    def as_flatdata(self):
         return {
            'provider': self.provider or 'Unknown Provider',
            'headers': self.headers(),
            'data': [x.flatdata() for x in self.results],
            }
