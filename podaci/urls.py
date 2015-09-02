from django.conf.urls import patterns, url
from django.views.generic import TemplateView

from core.auth import perm
from podaci import views

urlpatterns = patterns('',
    url(r'^$', perm('staff', TemplateView, template_name="podaci/tags/details.jinja"), name="podaci_info_home"),
    url(r'^search/$', views.Search.as_view(), name='podaci_search'),
    url(r'^file/$', views.FileList.as_view(), name='podaci_file_list'),
    url(r'^file/(?P<pk>[0-9]+)/$', views.FileDetail.as_view(), name='podaci_file_detail'),
    url(r'^file/create/$', views.FileUploadView.as_view(), name='podaci_file_create'),
    # url(r'^file/(?P<id>.+)/download/$', views.FileDownload.as_view(), name='podaci_file_download'),

    url(r'^tag/$', views.TagList.as_view(), name='podaci_tag_list'),
    url(r'^tag/(?P<pk>[0-9]+)/$', views.TagDetail.as_view(), name='podaci_tag_detail'),

    url(r'^collection/$', views.CollectionList.as_view(), name='podaci_collection_list'),
    url(r'^collection/(?P<pk>[0-9]+)/$', views.CollectionDetail.as_view(), name='podaci_collection_detail'),
)
