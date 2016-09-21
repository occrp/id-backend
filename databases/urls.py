from django.conf.urls import url

from .views import index, country, topic

app_name = 'databases'
urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^countries/(?P<country_code>\w+?)$', country, name='country'),
    url(r'^topics/(?P<db_type>\w+?)$', topic, name='topic')
]
