from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from core.auth import perm

import search.views

urlpatterns = patterns('',
    url(r'^$',               perm('any',  search.views.CombinedSearchHandler), name='search'),
    url(r'^results/$',       perm('user', search.views.SearchCheck), name='search_results'),
    url(r'^documents/$',	 perm('any',  search.views.DocumentSearchTemplate), name='search_documents'),
    url(r'^entities/$',      perm('any',  search.views.CombinedSearchHandler), name='search_entities'), # still needed for ajax only

    url(r'^images/$',        perm('user', search.views.ImageSearchTemplate), name='search_images'),
    url(r'^images/query/$',  perm('user', search.views.SearchImageQuery), name='search_images_query'),

    url(r'^social/$',        perm('user', TemplateView, template_name='search/search_social.jinja'), name='search_social'),
    url(r'^social/query/$',  perm('user', search.views.SearchSocialQuery), name='search_social_query'),
)


