from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from core.auth import perm

from id import search as oldsearch
import search.views

urlpatterns = patterns('',
    url(r'^$',               perm('any', oldsearch.CombinedSearchHandler), name='search'),
    url(r'^results/$',       perm('user', search.views.SearchCheck), name='search_results'),
    url(r'^entities/$',      perm('any', oldsearch.CombinedSearchHandler), name='search_entities'), # still needed for ajax only
    url(r'^images/$',        perm('user', TemplateView, template_name="search/search_images.jinja"), name='search_images'),
    url(r'^images/query/$',  perm('user', search.views.SearchImageQuery), name='search_images_query'),

    url(r'^social/$',        perm('user', TemplateView, template_name='search/search_social.jinja'), name='search_social'),
    url(r'^social/query/$',  perm('user', search.views.SearchSocialQuery), name='search_social_query'),
)


