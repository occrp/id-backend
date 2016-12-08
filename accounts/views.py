import urllib
import logging
from urlparse import urljoin
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.contrib.auth.views import logout as django_logout
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.conf import settings


logger = logging.getLogger(__name__)


def logout(request):
    django_logout(request)
    return HttpResponseRedirect('/')


def login(request, **kwargs):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')
    else:
        next_url = urllib.quote(request.GET.get('next', '/'))
        url = reverse('social:begin', kwargs={'backend': 'keycloak'})
        url = '%s?next=%s' % (url, next_url)
        return HttpResponseRedirect(url)


def profile(request, **kwargs):
    realm = '/auth/realms/%s/account/' % settings.KEYCLOAK_REALM
    return HttpResponseRedirect(urljoin(settings.KEYCLOAK_URL, realm))


class ProfileSetLanguage(TemplateView):
    # template_name = 'registration/profile.jinja'

    def get(self, request, lang, **kwargs):
        if lang in [x[0] for x in settings.LANGUAGES]:
            request.session['django_language'] = lang
            if request.user.is_authenticated():
                request.user.locale = lang
                request.user.save()
        go = request.GET.get("go", None)
        if not go and "HTTP_REFERER" in request.META:
            go = request.META["HTTP_REFERER"]
        if not go:
            go = "/"
        return HttpResponseRedirect(go)


class UserSuggest(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        prefix = self.request.REQUEST.get("prefix", "")
        res = {'prefix': prefix, 'results': []}
        q = Q(email__istartswith=prefix) | Q(first_name__istartswith=prefix) | \
            Q(last_name__istartswith=prefix)
        for obj in get_user_model().objects.filter(q)[:10]:
            res['results'].append({
                'id': obj.id,
                'display_name': obj.display_name
            })
        return JsonResponse(res)
