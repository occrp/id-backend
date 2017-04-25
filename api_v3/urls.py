from django.conf.urls import include, url
from rest_framework import routers

from .views import(
    SessionEndpoint,
    TicketsEndpoint,
    UsersEndpoint
)


router = routers.DefaultRouter(trailing_slash=False)
router.register(r'tickets', TicketsEndpoint)
router.register(r'users', UsersEndpoint)

urlpatterns = [
    url(r'^me/$', SessionEndpoint.as_view()),
    url(r'^', include(router.urls)),
]
