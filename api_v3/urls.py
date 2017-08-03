import os.path

from django.conf import urls, settings
from rest_framework import routers

from .views import(
    SessionEndpoint,
    TicketsEndpoint,
    ProfilesEndpoint,
    AttachmentsEndpoint,
    ActivitiesEndpoint,
    CommentsEndpoint,
    RespondersEndpoint,
    OpsEndpoint
)


router = routers.DefaultRouter(trailing_slash=False)
router.register(r'tickets', TicketsEndpoint)
router.register(r'profiles', ProfilesEndpoint)
router.register(r'attachments', AttachmentsEndpoint)
router.register(r'comments', CommentsEndpoint)
router.register(r'activities', ActivitiesEndpoint)
router.register(r'responders', RespondersEndpoint)
router.register(r'me', SessionEndpoint, base_name='me')
router.register(r'ops', OpsEndpoint, base_name='ops')

urlpatterns = [
    urls.url(r'^', urls.include(router.urls)),
]
