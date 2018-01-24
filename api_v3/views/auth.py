import urllib

from django.http import HttpResponseRedirect
from django.contrib.auth.views import logout as django_logout
from django.core.urlresolvers import reverse
from rest_framework import viewsets, permissions


class LogoutEndpoint(viewsets.GenericViewSet):

    def list(self, request, *args, **kwargs):
        django_logout(request)
        redirect_location = urllib.quote(request.GET.get('next') or '/')
        return HttpResponseRedirect(redirect_location)


class LoginEndpoint(viewsets.GenericViewSet):

    permission_classes = (permissions.AllowAny,)

    def list(self, request, *args, **kwargs):
        redirect_location = urllib.quote(request.GET.get('next') or '/')

        if request.user.is_authenticated():
            return HttpResponseRedirect(redirect_location)

        url_params = {'backend': 'keycloak'}
        url = reverse('social:begin', kwargs=url_params)
        url = '{}?{}'.format(url, urllib.urlencode({'next': redirect_location}))

        return HttpResponseRedirect(redirect_location)
