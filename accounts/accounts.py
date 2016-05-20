from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from registration.signals import user_registered

from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.views.generic import TemplateView, UpdateView, ListView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model # as per https://docs.djangoproject.com/en/dev/topics/auth/customizing/#referencing-the-user-model
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from django.db import IntegrityError

from settings.settings import LANGUAGES
from core.mixins import MessageMixin

from id.models import Profile, AccountRequest
from .forms import ProfileUpdateForm, ProfileBasicsForm, ProfileDetailsForm, ProfileAdminForm


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
    form_class = ProfileUpdateForm

    def get_success_url(self):
        return "/accounts/profile/%s" % self.get_object().email

    def get_object(self):
        if self.request.user.is_superuser:
            if self.kwargs.has_key("pk"):
                return get_user_model().objects.get(id=self.kwargs["pk"])
            elif self.kwargs.has_key("email"):
                return get_user_model().objects.get(email=self.kwargs["email"])
        return self.request.user

    def get_context_data(self, form):
        obj = self.get_object()
        ctx = super(ProfileUpdate, self).get_context_data()
        ctx["profile"] = obj
        ctx["editing_self"] = obj == self.request.user
        if self.request.method == "POST":
            ctx["form"] = ProfileUpdateForm(self.request.POST, instance=obj)
            if ctx["form"].is_valid():
                obj = ctx["form"].save()
            else:
                print ctx["form"].errors
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
    template_name = 'accessrequest/create.jinja'

    def get_context_data(self):
        request_type = self.request.GET.get("access_type", None)
        if not request_type:
            return {
                "requested_requester": AccountRequest.objects.filter(user=self.request.user, request_type="requester").count() >= 1,
                "requested_volunteer": AccountRequest.objects.filter(user=self.request.user, request_type="volunteer").count() >= 1,
                "is_requester": self.request.user.is_user,
                "is_volunteer": self.request.user.is_volunteer,
            }

        try:
            req = AccountRequest(request_type=request_type, user=self.request.user)
            req.save()
        except IntegrityError, e:
            pass

        return {
            "status": True,
            "requested_requester": AccountRequest.objects.filter(user=self.request.user, request_type="requester").count() >= 1,
            "requested_volunteer": AccountRequest.objects.filter(user=self.request.user, request_type="volunteer").count() >= 1,
            "is_requester": self.request.user.is_user,
            "is_volunteer": self.request.user.is_volunteer,
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
