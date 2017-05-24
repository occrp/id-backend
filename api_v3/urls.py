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
router.register(r'me', SessionEndpoint, base_name='me')

urlpatterns = [
    url(r'^', include(router.urls)),
]
