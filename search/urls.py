from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from core.auth import perm

import search.views

urlpatterns = patterns('',
    url(r'^old/$',           perm('any',  search.views.CombinedSearchHandler), name='search_old'),
    # url(r'^q/$',           perm('any',  search.views.HandleQuery), name='query'),

    url(r'^results/$',       perm('user', search.views.SearchCheck), name='search_results'),
    url(r'^document/$',      perm('any',  search.views.DocumentSearchTemplate), name='search'),
    # url(r'^$',               perm('any',  search.views.DocumentSearchTemplate), name='search'),
    url(r'^document/query/$',perm('any', search.views.DocumentSearchQuery), name='search_documents_query'),
    url(r'^entity/$',        perm('any',  search.views.CombinedSearchHandler), name='search_entities'), # still needed for ajax only

    url(r'^image/$',         perm('user', search.views.ImageSearchTemplate), name='search_images'),
    url(r'^image/query/$',   perm('user', search.views.SearchImageQuery), name='search_images_query'),

    url(r'^social/$',        perm('user', TemplateView, template_name='search/search_social.jinja'), name='search_social'),
    url(r'^social/query/$',  perm('user', search.views.SearchSocialQuery), name='search_social_query'),
)


