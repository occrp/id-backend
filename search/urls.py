from django.conf.urls import patterns, url
from django.views.generic import TemplateView

from core.auth import perm

import search.views

urlpatterns = patterns('',
    url(r'^document/$',      perm('any', search.views.DocumentSearchTemplate), name='search'),
    url(r'^document/query/$',perm('any', search.views.DocumentSearchQuery), name='search_documents_query'),

    url(r'^media/$',         perm('loggedin', search.views.MediaSearchTemplate), name='search_media'),
    url(r'^media/query/$',   perm('loggedin', search.views.SearchMediaQuery), name='search_media_query'),

    url(r'^social/$',        perm('user', TemplateView, template_name='search/search_social.jinja'), name='search_social'),
    url(r'^social/query/$',  perm('user', search.views.SearchSocialQuery), name='search_social_query'),
)
