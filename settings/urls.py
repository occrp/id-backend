from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from id import databases, requests, accounts
from id import validation, admin, tasks, errors
from core.auth import perm

from django.contrib.auth import views as auth_views
from registration.views import ActivationView

from core.views import NotificationSeen, NotificationStream
from id.views import ProfileRegistrationView, login, logout
from id.forms import ProfileRegistrationForm, FeedbackForm

js_info_dict = {
    'packages': ('id', 'ticket', 'search', 'podaci'),
}

urlpatterns = patterns('',
    url(r'^$',                              perm('any', TemplateView, template_name="splash.jinja"), name="home"),
    url(r'^about/id2/$',                    perm('any', TemplateView, template_name="about_id.jinja"), name='about_id'),
    url(r'^about/occrp/$',                  perm('any', TemplateView, template_name="about_us.jinja"), name='about_us'),

    url(r'^admin/$',                        perm('staff', admin.Panel), name='admin_panel'),
    url(r'^admin/scrapers/request/$',       perm('staff', admin.DatabaseScrapeRequestCreate), name='admin_scrapers_request'),
    url(r'^admin/budgets/$',                perm('staff', admin.Budgets), name='admin_budgets'),

    url(r'^admin/storage/$',                perm('admin', admin.Storage), name='admin_storage'),
    url(r'^admin/statistics/$',             perm('admin', admin.Statistics), name='statistics'),
    url(r'^feedback/$',                     perm('any', admin.Feedback), name='feedback'),
    url(r'^feedback/thankyou/$',            perm('any', admin.FeedbackThanks), name='feedback_thanks'),

    url(r'^databases/$',                    perm('any', databases.ExternalDatabaseList), name='externaldb_list'),
    url(r'^databases/add/$',                perm('staff', databases.ExternalDatabaseAdd), name='externaldb_add'),
    url(r'^databases/edit/(?P<id>[0-9]+)/$',perm('staff', databases.ExternalDatabaseEdit), name='externaldb_edit'),
    url(r'^databases/view/(?P<id>[0-9]+)/$',perm('any', databases.ExternalDatabaseDetail), name='externaldb_detail'),
    url(r'^databases/delete/(?P<id>[0-9]+)/$',
                                            perm('admin', databases.ExternalDatabaseDelete), name='externaldb_delete'),

    url(r'^accounts/login/$',               login, {'template_name': 'registration/login.jinja'}, name='login'),
    url(r'^accounts/logout/',               logout, {'template_name': 'registration/logout.jinja', 'fallback_redirect_url': '/accounts/login/'}, name='logout'),
    url(r'^accounts/users/$',               perm('admin', accounts.UserList), name='userprofile_list'),
    url(r'^accounts/suggest/$',             perm('loggedin', accounts.UserSuggest), name='userprofile_suggest'),
    url(r'^accounts/request/$',             perm('any', accounts.AccessRequestCreate), name='request_access_create'),
    url(r'^accounts/request/list/$',        perm('admin', accounts.AccessRequestList), name='request_access_list'),
    url(r'^accounts/request/list/approved/$',perm('admin', accounts.AccessRequestListApproved), name='request_access_list_approved'),
    url(r'^accounts/request/list/denied/$', perm('admin', accounts.AccessRequestListDenied), name='request_access_list_denied'),
    url(r'^accounts/profile/$',             perm('loggedin', accounts.ProfileUpdate), name='profile'),
    url(r'^accounts/profile/(?P<pk>[0-9]+)/$',
                                            perm('admin', accounts.ProfileUpdate), name='profile'),
    url(r'^accounts/profile/(?P<email>.+)/$',
                                            perm('admin', accounts.ProfileUpdate), name='profile'),
    url(r'^accounts/setlanguage/(?P<lang>[a-zA-Z]{2})/$',
                                            perm('any', accounts.ProfileSetLanguage), name='account_set_language'),

    url(r'^accounts/password/change/$',      auth_views.password_change, {'template_name': 'registration/password_change_form.jinja'}, name='auth_password_change'),
    url(r'^accounts/password/change/done/$', auth_views.password_change_done, {'template_name': 'registration/password_change_done.jinja'}, name='auth_password_change_done'),
    url(r'^accounts/password/reset/$',       auth_views.password_reset, {'template_name': 'registration/password_reset_form.jinja'}, name='auth_password_reset'),
    url(r'^accounts/password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', auth_views.password_reset_confirm, {'template_name': 'registration/password_reset_confirm.jinja'}, name='auth_password_reset_confirm'),
    url(r'^accounts/password/reset/complete/$', auth_views.password_reset_complete, {'template_name': 'registration/password_reset_complete.jinja'}, name='auth_password_reset_complete'),
    url(r'^accounts/password/reset/done/$',  auth_views.password_reset_done, {'template_name': 'registration/password_reset_done.jinja'}, name='auth_password_reset_done'),

    url(r'^accounts/activate/complete/$',   TemplateView.as_view(template_name='registration/activation_complete.jinja'), name='registration_activation_complete'),
    url(r'^accounts/activate/(?P<activation_key>w+)/$', ActivationView.as_view(template_name='registration/activation_form.jinja'), name='registration_activate'),
    url(r'^accounts/register/$',            ProfileRegistrationView.as_view(template_name='registration/registration_form.jinja', form_class=ProfileRegistrationForm), name='registration_register'),
    url(r'^accounts/register/complete/$',   TemplateView.as_view(template_name='registration/registration_complete.jinja'), name='registration_complete'),
    url(r'^accounts/register/closed/$',     TemplateView.as_view(template_name='registration/registration_closed.jinja'), name='registration_disallowed'),
    url(r'^accounts/social/', include('social_auth.urls')),

    url(r'^notifications/seen/(?P<pk>([\d]+|all))/', perm('user', NotificationSeen), name='notification_seen'),
    url(r'^notifications/stream/', perm('user', NotificationStream), name='notification_stream'),
    url(r'^notifications/', perm('user', TemplateView, template_name='notifications.jinja'), name='notifications'),

    url(r'^search/', include('search.urls')),
    url(r'^ticket/', include('ticket.urls')),
    url(r'^podaci/', include('podaci.urls')),
    url(r'^projects/', perm('staff', TemplateView, template_name='projects.jinja'), name='projects'),
    url(r'^api/', include('projects.urls')),
    url(r'^robots/', include('robots.urls')),

    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
    url(r'^jsi18n/(?P<packages>\S+?)/$', 'django.views.i18n.javascript_catalog'),

    url(r'^json/all_users/$', requests.Select2AllHandler.as_view(), name='select2_all_users'),

    url(r'^captcha/', include('captcha.urls')),
)

handler400 = errors._400
handler401 = errors._401
handler403 = errors._403
handler404 = errors._403
handler500 = errors._500
