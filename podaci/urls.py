from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from podaci import search, info, files, tags

urlpatterns = patterns('',
    url(r'^$', info.Home.as_view(), name='podaci_info_home'),
    url(r'^help/$', info.Help.as_view(), name='podaci_info_help'),
    url(r'^search/$', search.Search.as_view(), name='podaci_search'),

    url(r'^info/status/$', info.Status.as_view(), name='podaci_info_status'),
    url(r'^info/statistics/$', info.Statistics.as_view(), name='podaci_info_statistics'),

    url(r'^file/create/$', files.Create.as_view(), name='podaci_files_create'),
    url(r'^file/(?P<id>.+)/delete/$', files.Delete.as_view(), name='podaci_files_delete'),
    url(r'^file/(?P<id>.+)/update/$', files.Update.as_view(), name='podaci_files_upload'),
    url(r'^file/(?P<id>.+)/download/$', files.Download.as_view(), name='podaci_files_download'),
    url(r'^file/(?P<id>.+)/$', files.Details.as_view(), name='podaci_files_details'),

    url(r'^tag/create/$', tags.Create.as_view(), name='podaci_tags_create'),
    url(r'^tag/list/$', tags.List.as_view(), name='podaci_tags_delete'),
    url(r'^tag/(?P<id>.+)/delete/$', tags.Delete.as_view(), name='podaci_tags_delete'),
    url(r'^tag/(?P<id>.+)/update/$', tags.Update.as_view(), name='podaci_tags_upload'),
    url(r'^tag/selection/zip/$', tags.Zip.as_view(), name='podaci_tags_zip'),
    url(r'^tag/(?P<id>.+)/zip/$', tags.Zip.as_view(), name='podaci_tags_zip'),
    url(r'^tag/(?P<id>.+)/$', tags.Details.as_view(), name='podaci_tags_details'),
)


