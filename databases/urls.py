from core.auth import perm
from django.conf.urls import patterns, url

from databases.views import ExternalDatabaseList, DatabaseRequest
import databases


urlpatterns = patterns('',
    url(r'^$',                     perm('any', ExternalDatabaseList), name='externaldb_list'),
    url(r'register$',              perm('staff', DatabaseRequest), name='database_register'),
    url(r'edit/(?P<db_id>\d+)$', perm('staff', DatabaseRequest), name='database_register'),
)
