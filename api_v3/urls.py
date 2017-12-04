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
    DownloadEndpoint,
    OpsEndpoint,
    TicketStatsEndpoint
)


router = routers.DefaultRouter(trailing_slash=False)
router.register(r'tickets', TicketsEndpoint)
router.register(r'profiles', ProfilesEndpoint)
router.register(r'attachments', AttachmentsEndpoint)
router.register(r'comments', CommentsEndpoint)
router.register(r'activities', ActivitiesEndpoint)
router.register(r'responders', RespondersEndpoint)
router.register(r'me', SessionEndpoint, base_name='me')
router.register(r'download', DownloadEndpoint, base_name='download')
router.register(r'ops', OpsEndpoint, base_name='ops')
router.register(r'ticket-stats', TicketStatsEndpoint, base_name='ticket_stats')

urlpatterns = [
    urls.url(r'^', urls.include(router.urls)),
]
