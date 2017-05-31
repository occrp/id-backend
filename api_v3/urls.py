import os.path

from django.conf import urls, settings
from rest_framework import routers

from .views import(
    SessionEndpoint,
    TicketsEndpoint,
    UsersEndpoint,
    AttachmentsEndpoint,
    ActivitiesEndpoint,
    CommentsEndpoint
)


router = routers.DefaultRouter(trailing_slash=False)
router.register(r'tickets', TicketsEndpoint)
router.register(r'users', UsersEndpoint)
router.register(r'attachments', AttachmentsEndpoint)
router.register(r'comments', CommentsEndpoint)
router.register(r'activities', ActivitiesEndpoint)
router.register(r'me', SessionEndpoint, base_name='me')

urlpatterns = [
    urls.url(r'^', urls.include(router.urls)),
] + urls.static.static(
    os.path.join(settings.DOCUMENT_PATH, '/'),
    document_root=os.path.abspath(settings.BASE_DIR)
)