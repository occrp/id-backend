from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from core.auth import perm

from robots.views import *

urlpatterns = patterns('',
    url(r'^$',      perm('admin', RobotIndex), name='robots_index'),
)


