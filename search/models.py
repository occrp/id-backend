from django.db import models
from settings.settings import AUTH_USER_MODEL # as per https://docs.djangoproject.com/en/dev/topics/auth/customizing/#referencing-the-user-model
from search.api import searchproviders, ImageSearchResult

SEARCH_TYPES = (
    ('image', 'Image search'),
    ('podaci', 'Document search'),
    ('osoba', 'Graph search')
)


class SearchRequest(models.Model):
    requester = models.ForeignKey(AUTH_USER_MODEL, blank=True)
    search_type = models.CharField(choices=SEARCH_TYPES)
    created = models.DateTimeField(auto_now_add=True)
    query = models.TextField()

    def initiate_search(self):
        for prov in searchproviders:
            provider = prov()
            provider.start(args=(self))

        return {"status": True, "searchid": self.id, "bots_started": len(searchproviders), "checkin_after": 500}

    def bots_total(self):
        return len(self.searchrunner_set.all())

    def bots_done(self):
        return len(self.searchrunner_set.filter(done=True))

    def is_done(self):
        return all([x.done for x in self.searchrunner_set.all()])

    def get_results(self):
        return self.searchresult_set.all()

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

