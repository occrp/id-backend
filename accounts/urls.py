from django.conf.urls import include, url

from core.auth import perm

from . import views

urlpatterns = [
    url(r'^login/$', views.login, {'template_name': 'login.jinja'}, name='login'),
    url(r'^logout/', views.logout, {}, name='logout'),
    url(r'^profile/', views.profile, {}, name='profile'),
    url(r'^suggest/$', perm('user', views.UserSuggest), name='userprofile_suggest'),
    url(r'^setlanguage/(?P<lang>[a-zA-Z]{2})/$', perm('any', views.ProfileSetLanguage), name='account_set_language'),
    url(r'^social/', include('social.apps.django_app.urls', namespace='social')),
]
