from django.conf.urls import patterns, url

from core.auth import perm
from databases.views import ExternalDatabaseList

urlpatterns = patterns('',
    url(r'^$', perm('any', ExternalDatabaseList), name='externaldb_list'),
)
