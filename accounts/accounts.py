import logging

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from django.views.generic import TemplateView, UpdateView, ListView
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.db import IntegrityError

from settings.settings import LANGUAGES

from .models import AccountRequest
from .forms import ProfileUpdateForm, ProfileBasicsForm
from .forms import ProfileDetailsForm, ProfileAdminForm

log = logging.getLogger(__name__)


class ProfileSetLanguage(TemplateView):
    template_name = 'registration/profile.jinja'

    def get(self, request, lang, **kwargs):
        if lang in [x[0] for x in LANGUAGES]:
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
    template_name = 'registration/profile.jinja'
    permission_classes = (IsAuthenticated,)
    form_class = ProfileUpdateForm

    def get_success_url(self):
        return "/accounts/profile/%s/" % self.get_object().id

    def get_object(self):
        if self.request.user.is_superuser:
            return get_user_model().objects.get(id=self.kwargs["pk"])
        if self.request.user.id != int(self.kwargs["pk"]):
            raise PermissionDenied
        return self.request.user

    def get_context_data(self, form):
        obj = self.get_object()
        ctx = super(ProfileUpdate, self).get_context_data()
        ctx["profile"] = obj
        ctx["editing_self"] = obj == self.request.user
        if self.request.method == "POST":
            ctx["form"] = ProfileUpdateForm(self.request.POST, instance=obj)
            if not ctx["form"].is_valid():
                log.error("Error: %r", ctx["form"].errors)
            else:
                obj = ctx["form"].save()
            ctx["form_basics"] = ProfileBasicsForm(self.request.POST, instance=obj)
            ctx["form_details"] = ProfileDetailsForm(self.request.POST, instance=obj)
            if self.request.user.is_superuser:
                ctx["form_admin"] = ProfileAdminForm(self.request.POST, instance=obj)
        else:
            ctx["form"] = ProfileUpdateForm(instance=obj)
            ctx["form_basics"] = ProfileBasicsForm(instance=obj)
            ctx["form_details"] = ProfileDetailsForm(instance=obj)
            if self.request.user.is_superuser:
                ctx["form_admin"] = ProfileAdminForm(instance=obj)
        return ctx


class UserList(ListView):
    model = get_user_model()
    paginate_by = 50
    template_name = 'auth/user_list.jinja'

    def get_queryset(self):
        filter_terms = self.request.REQUEST.get("filter_terms", "")
        if filter_terms:
            query = (Q(email__contains=filter_terms)
                     | Q(first_name__contains=filter_terms)
                     | Q(last_name__contains=filter_terms))
            return self.model.objects.filter(query)

        return self.model.objects.all()

    def get_context_data(self, **kwargs):
        context = super(UserList, self).get_context_data(**kwargs)
        context["filter_terms"] = self.request.REQUEST.get("filter_terms", "")
        return context


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


class AccessRequestCreate(TemplateView):
    permission_classes = (IsAuthenticated, )
    template_name = 'accessrequest/create.jinja'

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_anonymous:
            return HttpResponseRedirect('/')
        return super(AccessRequestCreate, self).dispatch(request, *args, **kwargs)

    def get_context_data(self):
        try:
            req = AccountRequest(user=self.request.user)
            req.save()
        except IntegrityError as e:
            log.exception(e)

        return {
            "status": True,
            "requested": AccountRequest.objects.filter(user=self.request.user).count() >= 1,
            "is_requester": self.request.user.is_user
        }


class AccessRequestList(ListView):
    template_name = 'accessrequest/list.jinja'
    model = AccountRequest

    def get_queryset(self):
        approve = self.request.GET.get("approve_req", None)
        deny = self.request.GET.get("deny_req", None)
        if approve:
            ar = AccountRequest.objects.get(id=approve)
            ar.approve()
        if deny:
            ar = AccountRequest.objects.get(id=deny)
            ar.reject()

        return AccountRequest.objects.filter(approved=None)


class AccessRequestListApproved(AccessRequestList):
    def get_queryset(self):
        return AccountRequest.objects.filter(approved=True)


class AccessRequestListDenied(AccessRequestList):
    def get_queryset(self):
        return AccountRequest.objects.filter(approved=False)
