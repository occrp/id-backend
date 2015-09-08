import logging
from django.db import models
from django.db.models import Sum
from jsonfield import JSONField

from settings.settings import AUTH_USER_MODEL
from search.searchers import SEARCHERS
from core.utils import json_default

log = logging.getLogger(__name__)

SEARCH_TYPES = (
    ('document', 'Document search'),
    ('media', 'Media search')
)


class SearchRequest(models.Model):
    requester = models.ForeignKey(AUTH_USER_MODEL, blank=True, null=True)
    provider = models.CharField(max_length=250, default='unknown')
    total_results = models.IntegerField(default=0)
    search_type = models.CharField(max_length=30, choices=SEARCH_TYPES)
    created = models.DateTimeField(auto_now_add=True)
    query = JSONField(dump_kwargs={'default': json_default})

    def to_json(self):
        fields = ("id", "provider", "total_results", "search_type", "created",
                  "query")
        return dict([(x, getattr(self, x)) for x in fields])

    @classmethod
    def construct(cls, query, provider, user, search_type):
        log.info("Tasking %r searchers: %r", provider, query)
        search = cls()
        try:
            searcher = cls.get_searcher(provider)
            if searcher is None or searcher.TYPE != search_type:
                raise TypeError('Invalid search provider: %r' % provider)
            search.query = query
            search.provider = provider
            search.search_type = search_type
            if not user.is_anonymous():
                search.requester = user
            search.save()

            results = searcher().run(search)
            search.total_results = results.total
            search.save()
            return {
                "status": True,
                "search": search.to_json(),
                "total": results.total,
                "results": [dict(r) for r in results]
            }
        except Exception as e:
            log.exception(e)
            return {
                "status": False,
                "search": search.to_json(),
                "message": unicode(e),
                "type": repr(e)
            }

    @classmethod
    def by_type(self, type_name):
        """ Get a list of searchers by name. """
        return [x.PROVIDER for x in SEARCHERS if x.TYPE == type_name]

    @classmethod
    def get_searcher(cls, name):
        """ Get a provider by name. """
        for searcher in SEARCHERS:
            if searcher.PROVIDER == name:
                return searcher

    @classmethod
    def statistics(cls):
        res = []
        for searcher in SEARCHERS:
            qs = SearchRequest.objects.filter(provider=searcher.PROVIDER)
            agg = qs.aggregate(Sum('total_results'))
            res.append({
                "type": searcher.PROVIDER,
                "count": qs.count(),
                "results": agg['total_results__sum'] or 0
            })
        agg = SearchRequest.objects.aggregate(Sum('total_results'))
        res.append({
            "type": "Total",
            "count": SearchRequest.objects.count(),
            "results": agg['total_results__sum'] or 0
        })
        return res
