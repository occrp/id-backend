from django.conf.urls import include, url
from django.views.generic import TemplateView
from django.views.i18n import javascript_catalog

import accounts.views
from core.manage import Panel
from core.admin import admin_site
from accounts.manage import Statistics
from core.auth import perm
from core.views import NotificationSeen, NotificationStream
from core.views import NotificationSubscriptions

# Instead of admin auto-discovery:
from databases.admin import ExternalDatabaseAdmin  # noqa
from accounts.admin import ProfileAdmin, NetworkAdmin  # noqa
from ticket.admin import BudgetAdmin  # noqa

js_info_dict = {
    'packages': ('ticket'),
}

urlpatterns = [
    url(r'^$', perm('any', TemplateView, template_name="splash.jinja"), name="home"),
    url(r'^about/id2/$', perm('any', TemplateView, template_name="about_id.jinja"), name='about_id'),
    url(r'^about/occrp/$', perm('any', TemplateView, template_name="about_us.jinja"), name='about_us'),
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^api/2/accounts/profile/$', accounts.views.Profile.as_view(), name='api_2_profile'),
    url(r'^api/2/notifications/$', NotificationSubscriptions.as_view(), name='api_2_notifications'),
    url(r'^api/2/notifications/seen/$', NotificationSeen.as_view(), name='api_2_notifications_seen'),
    url(r'^api/2/notifications/stream/$', NotificationStream.as_view(), name='api_2_notifications_stream'),

    url(r'^admin/', admin_site.urls),
    url(r'^manage/$', perm('staff', Panel), name='manage_panel'),
    url(r'^statistics/$', perm('admin', Statistics), name='statistics'),

    url(r'^accounts/', include('accounts.urls')),

    url(r'^notifications/seen/(?P<pk>([\d]+|all))/', perm('user', NotificationSeen), name='notification_seen'),
    url(r'^notifications/stream/', perm('user', NotificationStream), name='notification_stream'),

    url(r'^ticket/', include('ticket.urls')),
    url(r'^databases/', include('databases.urls')),

    # url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^jsi18n/$', javascript_catalog, js_info_dict),
    url(r'^jsi18n/(?P<packages>\S+?)/$', javascript_catalog),

    url(r'^captcha/', include('captcha.urls')),
]
