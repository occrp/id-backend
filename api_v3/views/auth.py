import urllib.parse

from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect
from django.urls import reverse
from django.contrib.auth.views import auth_logout
from rest_framework import viewsets, permissions
from social_django.utils import BACKENDS, module_member


class LogoutEndpoint(viewsets.ViewSet):
    permission_classes = (permissions.AllowAny,)

    def retrieve(self, request, pk=None):
        redirect_location = urllib.parse.quote(request.GET.get('next') or '/')
        response_factory = HttpResponsePermanentRedirect

        if str(request.user.id) == pk and request.user.is_authenticated:
            response_factory = HttpResponseRedirect
            auth_logout(request)

        return response_factory(redirect_location)


class LoginEndpoint(viewsets.ViewSet):
    permission_classes = (permissions.AllowAny,)

    def list(self, request, *args, **kwargs):
        redirect_location = urllib.parse.quote(request.GET.get('next') or '/')

        if request.user.is_authenticated:
            return HttpResponseRedirect(redirect_location)

        backend = 'NOT-CONFIGURED'
        backends = [module_member(b) for b in BACKENDS]

        if backends:
            backend = backends[0].name

        path = '?'.join([
            reverse('social:begin', kwargs={'backend': backend}),
            urllib.parse.urlencode({'next': redirect_location})
        ])

        return HttpResponseRedirect(path)
