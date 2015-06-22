from django.conf.urls import patterns, include, url
from projects.views import dummy_view


urlpatterns = patterns('',
    url(r'^project_create/$',                        dummy_view, name='project_create'),
    url(r'^project_list/$',                          dummy_view, name='project_list'),
)