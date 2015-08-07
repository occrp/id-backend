from django.conf.urls import patterns, include, url
from podaci import views
from django.views.generic import TemplateView
from core.auth import perm

urlpatterns = patterns('',
    url(r'^$', perm('any', TemplateView, template_name="podaci/tags/details.jinja"), name="podaci_info_home"),
    url(r'^search/$', views.Search.as_view(), name='podaci_search'),
    url(r'^file/$', views.FileList.as_view(), name='podaci_file_list'),
    url(r'^file/(?P<pk>[0-9]+)/$', views.FileDetail.as_view(), name='podaci_file_detail'),
    # url(r'^file/(?P<id>.+)/download/$', views.FileDownload.as_view(), name='podaci_file_download'),

    url(r'^tag/$', views.TagList.as_view(), name='podaci_tag_list'),
    url(r'^tag/(?P<pk>[0-9]+)/$', views.TagDetail.as_view(), name='podaci_tag_detail'),

    url(r'^collection/$', views.CollectionList.as_view(), name='podaci_collection_list'),
    url(r'^collection/(?P<pk>[0-9]+)/$', views.CollectionDetail.as_view(), name='podaci_collection_detail'),

    #url(r'^tag/selection/overview/$',      perm("staff", tags.Overview), name='podaci_tags_overview'),
    # url(r'^tag/(?P<id>.+)/overview/$',     perm("staff", tags.Overview), name='podaci_tags_overview'),
)
