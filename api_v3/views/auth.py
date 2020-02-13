import urllib.parse

from django.http import HttpResponseRedirect
from django.urls import reverse
from rest_framework import viewsets, permissions
from social_django.utils import BACKENDS, module_member


class LoginEndpoint(viewsets.GenericViewSet):
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
