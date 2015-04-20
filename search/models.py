from django.db import models
from settings.settings import AUTH_USER_MODEL # as per https://docs.djangoproject.com/en/dev/topics/auth/customizing/#referencing-the-user-model

class SearchRequest(models.Model):
    requester = models.ForeignKey(AUTH_USER_MODEL)
    created = models.DatetimeField(auto_now_add=True)
    completed = models.DatetimeField(blank=True)
    done = models.BooleanField()
    query = models.TextField()

class SearchResult(models.Model):
    request = models.ForeignKey(SearchRequest)
    provider = models.CharField(max_length=30)
    found = models.DatetimeField(auto_now_add=True)
    data = models.TextField()

