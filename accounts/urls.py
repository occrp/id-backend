from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from registration.views import ActivationView

from core.auth import perm
from core.views import NotificationSeen, NotificationStream, NotificationSubscriptions, Notify, AuditLogView
from databases.views import DatabaseCollectionView, DatabaseMemberView
import databases.admin as databases_admin

from . import accounts, forms, views

urlpatterns = patterns('',
    url(r'^login/$',               views.login, {'template_name': 'registration/login.jinja'}, name='login'),
    url(r'^logout/',               views.logout, {'template_name': 'registration/logout.jinja', 'fallback_redirect_url': '/accounts/login/'}, name='logout'),
    url(r'^users/$',               perm('admin', accounts.UserList), name='userprofile_list'),
    url(r'^suggest/$',             perm('loggedin', accounts.UserSuggest), name='userprofile_suggest'),
    url(r'^request/$',             perm('any', accounts.AccessRequestCreate), name='request_access_create'),
    url(r'^request/list/$',        perm('admin', accounts.AccessRequestList), name='request_access_list'),
    url(r'^request/list/approved/$',perm('admin', accounts.AccessRequestListApproved), name='request_access_list_approved'),
    url(r'^request/list/denied/$', perm('admin', accounts.AccessRequestListDenied), name='request_access_list_denied'),
    url(r'^profile/$',             perm('loggedin', accounts.ProfileUpdate), name='profile'),
    url(r'^profile/(?P<pk>[0-9]+)/$',
                                            perm('admin', accounts.ProfileUpdate), name='profile'),
    url(r'^profile/(?P<email>.+)/$',
                                            perm('admin', accounts.ProfileUpdate), name='profile'),
    url(r'^setlanguage/(?P<lang>[a-zA-Z]{2})/$',
                                            perm('any', accounts.ProfileSetLanguage), name='account_set_language'),

    url(r'^password/change/$',      auth_views.password_change, {'template_name': 'registration/password_change_form.jinja'}, name='password_change'),
    url(r'^password/change/done/$', auth_views.password_change_done, {'template_name': 'registration/password_change_done.jinja'}, name='password_change_done'),
    url(r'^password/reset/$',       auth_views.password_reset, {'template_name': 'registration/password_reset_form.jinja'}, name='password_reset'),
    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', auth_views.password_reset_confirm, {'template_name': 'registration/password_reset_confirm.jinja'}, name='password_reset_confirm'),
    url(r'^password/reset/complete/$', auth_views.password_reset_complete, {'template_name': 'registration/password_reset_complete.jinja'}, name='password_reset_complete'),
    url(r'^password/reset/done/$',  auth_views.password_reset_done, {'template_name': 'registration/password_reset_done.jinja'}, name='password_reset_done'),

    url(r'^activate/complete/$',   TemplateView.as_view(template_name='registration/activation_complete.jinja'), name='registration_activation_complete'),
    url(r'^activate/(?P<activation_key>w+)/$', ActivationView.as_view(template_name='registration/activation_form.jinja'), name='registration_activate'),
    url(r'^register/$',            views.ProfileRegistrationView.as_view(template_name='registration/registration_form.jinja', form_class=forms.ProfileRegistrationForm), name='registration_register'),
    url(r'^register/complete/$',   TemplateView.as_view(template_name='registration/registration_complete.jinja'), name='registration_complete'),
    url(r'^register/closed/$',     TemplateView.as_view(template_name='registration/registration_closed.jinja'), name='registration_disallowed'),
    url(r'^social/', include('social.apps.django_app.urls', namespace='social')),
)

