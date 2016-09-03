from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

import accounts.views
import accounts.admin
import core.admin
from core.auth import perm
from core.views import NotificationSeen, NotificationStream
from core.views import NotificationSubscriptions, Notify
from databases.views import DatabaseCollectionView, DatabaseMemberView
import podaci
import ticket.admin


from . import errors

js_info_dict = {
    'packages': ('ticket', 'search', 'podaci'),
}

urlpatterns = patterns('',
    url(r'^$', perm('any', TemplateView, template_name="splash.jinja"), name="home"),
    url(r'^about/id2/$', perm('any', TemplateView, template_name="about_id.jinja"), name='about_id'),
    url(r'^about/occrp/$', perm('any', TemplateView, template_name="about_us.jinja"), name='about_us'),
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^api/2/accounts/profile/$', accounts.views.Profile.as_view(), name='api_2_profile'),
    url(r'^api/2/notifications/$', NotificationSubscriptions.as_view(), name='api_2_notifications'),
    url(r'^api/2/notifications/seen/$', NotificationSeen.as_view(), name='api_2_notifications_seen'),
    url(r'^api/2/notifications/stream/$', NotificationStream.as_view(), name='api_2_notifications_stream'),
    url(r'^api/2/notifications/notify/$', Notify.as_view(), name='api_2_notifications_notify'),
    url(r'^api/2/databases/$', DatabaseCollectionView.as_view(), name='api_2_databases_collection'),
    url(r'^api/2/databases/(?P<pk>\d+)$', DatabaseMemberView.as_view(), name='api_2_databases_member'),

    url(r'^admin/$', perm('staff', core.admin.Panel), name='admin_panel'),
    url(r'^admin/budgets/$', perm('staff', ticket.admin.Budgets), name='admin_budgets'),
    url(r'^admin/statistics/$', perm('admin', accounts.admin.Statistics), name='statistics'),

    url(r'^feedback/', include('feedback.urls')),
    url(r'^accounts/', include('accounts.urls')),

    url(r'^notifications/seen/(?P<pk>([\d]+|all))/', perm('user', NotificationSeen), name='notification_seen'),
    url(r'^notifications/stream/', perm('user', NotificationStream), name='notification_stream'),
    url(r'^notifications/', perm('user', TemplateView, template_name='notifications.jinja'), name='notifications'),

    url(r'^ticket/', include('ticket.urls')),
    url(r'^databases/', include('databases.urls')),

    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
    url(r'^jsi18n/(?P<packages>\S+?)/$', 'django.views.i18n.javascript_catalog'),

    url(r'^captcha/', include('captcha.urls')),
)

handler400 = errors._400
handler401 = errors._401
handler403 = errors._403
handler404 = errors._404
handler500 = errors._500
