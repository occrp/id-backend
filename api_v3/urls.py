from django.conf.urls import url

from .views import SessionEndpoint

urlpatterns = [
    url(r'^me/$', SessionEndpoint.as_view(), name='api_3_me'),
]
