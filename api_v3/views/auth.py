import urllib

from django.http import HttpResponseRedirect
from django.urls import reverse
from rest_framework import viewsets, permissions
from social_django.utils import BACKENDS, module_member


class LoginEndpoint(viewsets.GenericViewSet):
    permission_classes = (permissions.AllowAny,)

    def list(self, request, *args, **kwargs):
        redirect_location = urllib.quote(request.GET.get('next') or '/')

        if request.user.is_authenticated():
            return HttpResponseRedirect(redirect_location)

        backend = u'NOT-CONFIGURED'
        backends = map(lambda b: module_member(b), BACKENDS)

        if backends:
            backend = backends[0].name

        path = '?'.join([
            reverse('social:begin', kwargs={'backend': backend}),
            urllib.urlencode({'next': redirect_location})
        ])

        return HttpResponseRedirect(path)
