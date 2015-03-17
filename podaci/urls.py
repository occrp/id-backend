from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from podaci import search, info, files, tags
from id.decorators import perm

urlpatterns = patterns('',
    url(r'^$',                             perm("staff", info.Home), name='podaci_info_home'),
    url(r'^help/$',                        perm("staff", info.Help), name='podaci_info_help'),
    url(r'^search/$',                      perm("staff", search.Search), name='podaci_search'),
    url(r'^search/mention/$',              perm("staff", search.SearchMention), name='podaci_search_mention'),

    url(r'^info/status/$',                 perm("admin", info.Status), name='podaci_info_status'),
    url(r'^info/statistics/$',             perm("admin", info.Statistics), name='podaci_info_statistics'),

    url(r'^file/create/$',                 perm("staff", files.Create), name='podaci_files_create'),
    url(r'^file/(?P<id>.+)/note/add/$',    perm("staff", files.NoteAdd), name='podaci_files_note_add'),
    url(r'^file/(?P<id>.+)/note/delete/$', perm("staff", files.NoteDelete), name='podaci_files_note_add'),
    url(r'^file/(?P<id>.+)/note/update/$', perm("staff", files.NoteUpdate), name='podaci_files_note_add'),
    url(r'^file/(?P<id>.+)/delete/$',      perm("staff", files.Delete), name='podaci_files_delete'),
    url(r'^file/(?P<id>.+)/update/$',      perm("staff", files.Update), name='podaci_files_upload'),
    url(r'^file/(?P<id>.+)/download/$',    perm("staff", files.Download), name='podaci_files_download'),
    url(r'^file/(?P<id>.+)/$',             perm("staff", files.Details), name='podaci_files_details'),

    url(r'^tag/create/$',                  perm("staff", tags.Create), name='podaci_tags_create'),
    url(r'^tag/list/$',                    perm("staff", tags.List), name='podaci_tags_list'),
    url(r'^tag/(?P<id>.+)/delete/$',       perm("staff", tags.Delete), name='podaci_tags_delete'),
    url(r'^tag/(?P<id>.+)/update/$',       perm("staff", tags.Update), name='podaci_tags_upload'),
    url(r'^tag/selection/zip/$',           perm("staff", tags.Zip), name='podaci_tags_zip'),
    url(r'^tag/(?P<id>.+)/zip/$',          perm("staff", tags.Zip), name='podaci_tags_zip'),
    url(r'^tag/(?P<id>.+)/$',              perm("staff", tags.Details), name='podaci_tags_details'),
)


