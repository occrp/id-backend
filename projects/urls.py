from django.conf.urls import patterns, include, url
from projects.views import dummy_view


urlpatterns = patterns('',
    url(r'^project/create/$',                        dummy_view, name='project_create'),
    url(r'^project/list/$',                          dummy_view, name='project_list'),
    url(r'^project/(?P<id>.+)/$',                    dummy_view, name='project_get'),
    url(r'^project/(?P<id>.+)/alter/$',                    dummy_view, name='project_alter'),
    url(r'^project/(?P<id>.+)/delete/$',             dummy_view, name='project_delete'),
    url(r'^project/(?P<id>.+)/add_users/$',             dummy_view, name='project_add_users'),
    url(r'^project/(?P<id>.+)/remove_users/$',             dummy_view, name='project_remove_users')

)