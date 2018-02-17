from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

from .views.auth import LoginEndpoint, LogoutEndpoint
from .views.attachments import AttachmentsEndpoint
from .views.activities import ActivitiesEndpoint
from .views.comments import CommentsEndpoint
from .views.download import DownloadEndpoint
from .views.ops import OpsEndpoint
from .views.profiles import ProfilesEndpoint
from .views.responders import RespondersEndpoint
from .views.session import SessionEndpoint
from .views.subscribers import SubscribersEndpoint
from .views.tickets import TicketsEndpoint
from .views.ticket_stats import TicketStatsEndpoint


router = DefaultRouter()
router.register(r'attachments', AttachmentsEndpoint)
router.register(r'activities', ActivitiesEndpoint)
router.register(r'comments', CommentsEndpoint)
router.register(r'download', DownloadEndpoint, base_name='download')
router.register(r'login', LoginEndpoint, base_name='login')
router.register(r'logout', LogoutEndpoint, base_name='login')
router.register(r'me', SessionEndpoint, base_name='me')
router.register(r'ops', OpsEndpoint, base_name='ops')
router.register(r'profiles', ProfilesEndpoint)
router.register(r'responders', RespondersEndpoint)
router.register(r'subscribers', SubscribersEndpoint)
router.register(r'tickets', TicketsEndpoint)
router.register(r'ticket-stats', TicketStatsEndpoint, base_name='ticket_stats')

urlpatterns = [
    url('api/v3/', include(router.urls)),
    url('', include('social_django.urls', namespace='social'))
]
