from id.apis.elastic import elastic
# from id.apis.googledrive import drive_decorator, Drive
from id.apis import opencorporates
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify


SEARCH_PROVIDERS = []

def register_provider(provider):
    SEARCH_PROVIDERS.append(provider)

def get_defaults():
    return [x.provider_id for x in SEARCH_PROVIDERS if x.provider_default]

def get_providers_names():
    return [(x.provider_id, x.provider_name) for x in SEARCH_PROVIDERS]

class SearchResultList(object):
    """
    contains results to be displayed on the ID search results page.
    The results are in an iterable; it can contain any kind of object, provided
    this can be synchronised with a display template.

    result_type should have a corresponding macro in search_base

    Paging and access control should have been applied prior to creating
    this object.
    """
    offset = 0
    limit = 0
    result_type = None
    result_count = None

    def __init__(self, results, result_type,
                 offset=0, limit=None, result_count=None):
        self.offset = offset
        self.limit = limit or len(results)
        self.results = results
        self.result_type = result_type
        self.result_count = result_count or len(self.results)


class SearchProvider(object):
    result_type = None # override in Subclass
    result_count = None
    provider_id = None      # MUST BE UNIQUE!
    provider_name = None
    provider_description = None
    provider_default = False

    def __init__(self):
        pass

    def search(self, query, offset, limit, **kwargs):
        raw_results = self._search(query, offset, limit, **kwargs)
        if self.result_count is None:
            # best to set this in search in subclasses
            self.result_count = len(raw_results)
        self.results = SearchResultList(
            results=raw_results,
            result_type=self.result_type,
            result_count=self.result_count,
            offset=offset,
            limit=limit)


#class DocumentSearch(SearchProvider):
#    result_type = 'documents'
#
#    def search(self, query, offset, limit, **kwargs):
#        return Drive.system_instance().search(
#            query)[offset:offset+limit]

class OpenCorporatesSearchCompanies(SearchProvider):
    result_type = 'Companies from OpenCorporates'
    searcher = opencorporates.OpenCorpSearch()
    provider_id = 'opencorporates'
    provider_name = _('OpenCorporates')
    provider_description = _('Companies from OpenCorporates')
    provider_default = False

    def _search(self, query, offset, limit, **kwargs):
        results = self.searcher.search(query, offset, limit)
        self.result_count = results.resultcount
        return results.resultdata


class ElasticSearch(SearchProvider):
    result_type = 'elasticsearch'
    es_index = 'id_prod'
    provider_id = 'elasticsearch'
    provider_name = _('Documents')
    provider_description = _('ID document database')
    provider_default = True

    def _search(self, query, offset, limit, **kwargs):
        results = elastic.search(query,offset=offset,
                                 limit=limit,
                                 index='id_prod', **kwargs)
        self.result_count = results['hits']['total']
        return results['hits']['hits']


class EntitySearch(SearchProvider):
    result_type = 'entities'
    provider_id = 'entities'
    provider_name = _('Entities')
    provider_description = _('People, companies and more')
    provider_default = True

    def _search(self, query, offset, limit, **kwargs):
        # XXX this isn't escaped properly
        # XXX needs work on access controls
        # XXX offset/limit are inefficient
        index = kwargs.get('index', 'all')

        # temporarily disable entities for non-admins in search results
        # XXX this is a temporary fix, until we get proper entity access
        # control
        #if not has_perms(['admin', 'staff']):
        #    return []

        try:
            results = (search.Index(get_index_version(index))
                       .search(query))
        except:
            results = []
        finally:
            results = ndb.get_multi([ndb.Key(urlsafe=r.doc_id) for
                                     r in results])
        self.result_count = len(results)
        return results[offset:offset+limit]


register_provider(OpenCorporatesSearchCompanies)
register_provider(ElasticSearch)
# register_provider(EntitySearch)
