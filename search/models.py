from django.db import models
from settings.settings import AUTH_USER_MODEL # as per https://docs.djangoproject.com/en/dev/topics/auth/customizing/#referencing-the-user-model
from search.api import searchproviders, ImageSearchResult
from core.utils import json_dumps, json_loads

SEARCH_TYPES = (
    ('image', 'Image search'),
    ('podaci', 'Document search'),
    ('osoba', 'Graph search')
)


class SearchRequest(models.Model):
    requester = models.ForeignKey(AUTH_USER_MODEL, blank=True)
    search_type = models.CharField(max_length=30, choices=SEARCH_TYPES)
    created = models.DateTimeField(auto_now_add=True)
    query = models.TextField()

    def initiate_search(self, limit_providers=None):
        for prov in self.get_providers(limit_providers):
            provider = prov()
            provider.start(self)

        return {"status": True, "searchid": self.id, "bots_started": len(searchproviders), "checkin_after": 500}

    def bots_total(self):
        return len(self.searchrunner_set.all())

    def bots_done(self):
        return len(self.searchrunner_set.filter(done=True))

    def is_done(self):
        return all([x.done for x in self.searchrunner_set.all()])

    def get_results(self):
        return [
            x.as_json() for x in self.searchresult_set.all()
        ]

    def create_runner(self, name):
        runner = SearchRunner()
        runner.request = self
        runner.name = name
        runner.save()
        return runner

    def create_result(self, provider, data):
        res = SearchResult()
        res.request = self
        res.provider = provider
        res.data = json_dumps(data)
        res.save()
        return res

    def list_providers(self):
        """Get a list of providers by name."""
        return [x.PROVIDER for x in searchproviders]

    def get_providers(self, limit_to=None):
        """Get the providers."""
        if not limit_to:
            return searchproviders
        return [x for x in searchproviders if x.PROVIDER in limit_to]


class SearchRunner(models.Model):
    request = models.ForeignKey(SearchRequest)
    name = models.CharField(max_length=30)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    results = models.IntegerField(default=0)
    done = models.BooleanField(default=False)


class SearchResult(models.Model):
    request = models.ForeignKey(SearchRequest)
    provider = models.CharField(max_length=30)
    found = models.DateTimeField(auto_now_add=True)
    data = models.TextField()

    def as_json(self):
        return {
            "provider": self.provider,
            "found": self.found,
            "data": json_loads(self.data)
        }
