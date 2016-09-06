from core.auth import perm
from django.conf.urls import url

from .views import index

app_name = 'databases'
urlpatterns = [
    url(r'^$', index, name='index')
]
