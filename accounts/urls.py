from django.conf.urls import include, url
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views

from core.auth import perm

from . import accounts, forms, views

urlpatterns = [
    url(r'^login/$', views.login, {'template_name': 'login.jinja'},
        name='login'),
    url(r'^logout/', views.logout, {}, name='logout'),
    url(r'^suggest/$',
        perm('user', accounts.UserSuggest), name='userprofile_suggest'),
    url(r'^profile/$', perm('user', accounts.ProfileUpdate), name='profile'),
    url(r'^setlanguage/(?P<lang>[a-zA-Z]{2})/$',
        perm('any', accounts.ProfileSetLanguage), name='account_set_language'),

    url(r'^password/reset/$', auth_views.password_reset,
        {'template_name': 'password_reset_form.jinja'},
        name='password_reset'),
    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm,
        {'template_name': 'password_reset_confirm.jinja'},
        name='password_reset_confirm'),
    url(r'^password/reset/complete/$', auth_views.password_reset_complete,
        {'template_name': 'password_reset_complete.jinja'},
        name='password_reset_complete'),
    url(r'^password/reset/done/$', auth_views.password_reset_done,
        {'template_name': 'password_reset_done.jinja'},
        name='password_reset_done'),

    url(r'activate/(?P<activation_key>\w+)/$',
        views.ProfileActivationView.as_view(template_name='activation_form.jinja'),
        name='registration_activate'),
    url(r'^register/$',
        views.ProfileRegistrationView.as_view(template_name='registration_form.jinja',
                                              form_class=forms.ProfileRegistrationForm),
        name='registration_register'),
    url(r'^register/complete/$',
        TemplateView.as_view(template_name='registration_complete.jinja'),
        name='registration_complete'),
    url(r'^social/', include('social.apps.django_app.urls', namespace='social')),
]
