from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from podaci import search, info, files, tags
from core.auth import perm

urlpatterns = patterns('',
)


