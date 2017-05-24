from django.conf.urls import include, url
from rest_framework import routers

from .views import(
    SessionEndpoint,
    TicketsEndpoint,
    UsersEndpoint,
    NotificationsEndpoint,
    AttachmentsEndpoint
)


router = routers.DefaultRouter(trailing_slash=False)
router.register(r'tickets', TicketsEndpoint)
router.register(r'users', UsersEndpoint)
router.register(r'notifications', NotificationsEndpoint)
router.register(r'attachments', AttachmentsEndpoint)

urlpatterns = [
    url(r'^me/$', SessionEndpoint.as_view()),
    url(r'^', include(router.urls)),
]
