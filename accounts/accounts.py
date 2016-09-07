import logging
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.views.generic import TemplateView, UpdateView
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.conf import settings

from .forms import ProfileUpdateForm

log = logging.getLogger(__name__)


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


class ProfileUpdate(UpdateView):
    template_name = 'profile.jinja'
    permission_classes = (IsAuthenticated,)
    form_class = ProfileUpdateForm

    def get_object(self):
        return self.request.user

    def get_context_data(self):
        obj = self.get_object()
        ctx = super(ProfileUpdate, self).get_context_data()
        ctx["profile"] = obj
        if self.request.method == "POST":
            ctx["form"] = ProfileUpdateForm(self.request.POST, instance=obj)
            if not ctx["form"].is_valid():
                log.error("Error: %r", ctx["form"].errors)
            else:
                obj = ctx["form"].save()
        else:
            ctx["form"] = ProfileUpdateForm(instance=obj)
        return ctx

    def get_success_url(self):
        return reverse('profile')


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
