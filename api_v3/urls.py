from pydoc import locate

from django.conf import settings
from django.conf.urls import include, url


from .views.auth import LoginEndpoint, LogoutEndpoint
from .views.attachments import AttachmentsEndpoint
from .views.activities import ActivitiesEndpoint
from .views.comments import CommentsEndpoint
from .views.download import DownloadEndpoint
from .views.expenses import ExpensesEndpoint
from .views.expense_exports import ExpenseExportsEndpoint
from .views.profiles import ProfilesEndpoint
from .views.responders import RespondersEndpoint
from .views.session import SessionEndpoint
from .views.subscribers import SubscribersEndpoint
from .views.tickets import TicketsEndpoint
from .views.ticket_stats import TicketStatsEndpoint
from .views.ticket_exports import TicketExportsEndpoint


router = locate(settings.ROUTER_CLASS)(trailing_slash=False)
router.register(r'attachments', AttachmentsEndpoint)
router.register(r'activities', ActivitiesEndpoint)
router.register(r'comments', CommentsEndpoint)
router.register(r'download', DownloadEndpoint, basename='download')
router.register(r'me', SessionEndpoint, basename='me')
router.register(r'profiles', ProfilesEndpoint)
router.register(r'responders', RespondersEndpoint)
router.register(r'subscribers', SubscribersEndpoint)
router.register(r'expenses', ExpensesEndpoint)
router.register(
    r'expense-exports',
    ExpenseExportsEndpoint,
    basename='expense_exports')
router.register(r'tickets', TicketsEndpoint)
router.register(r'ticket-stats', TicketStatsEndpoint, basename='ticket_stats')
router.register(
    r'ticket-exports',
    TicketExportsEndpoint,
    basename='ticket_exports')

auth_router = locate(settings.ROUTER_CLASS)(trailing_slash=False)
auth_router.register(r'login', LoginEndpoint, basename='login')
auth_router.register(r'logout', LogoutEndpoint, basename='logout')

urlpatterns = [
    url('api/v3/', include(router.urls)),
    url('accounts/', include(auth_router.urls)),
    url('accounts/social/', include('social_django.urls', namespace='social'))
]
