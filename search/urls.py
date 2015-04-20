from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from core.auth import perm

from id import search as oldsearch
import search.views

urlpatterns = patterns('',
    url(r'^$',             perm('any', oldsearch.CombinedSearchHandler), name='search'),
    url(r'^entities/$',    perm('any', oldsearch.CombinedSearchHandler), name='search_entities'), # still needed for ajax only
    url(r'^images/$',      perm('any', search.views.ImageSearch), name='search_images')
)


