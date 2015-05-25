from django.http import HttpResponseRedirect
from django.views.generic import *
from django.contrib.auth.decorators import login_required
#from django.contrib.auth.models import User
from django.contrib.auth import get_user_model # as per https://docs.djangoproject.com/en/dev/topics/auth/customizing/#referencing-the-user-model
from settings.settings import LANGUAGES
from django.utils.translation import ugettext_lazy as _
from registration.signals import user_registered

from core.mixins import MessageMixin

from id.models import Profile, AccountRequest
from id.forms import ProfileUpdateForm, ProfileBasicsForm, ProfileDetailsForm, ProfileAdminForm


class ProfileSetLanguage(TemplateView):
    template_name = 'registration/profile.jinja'

    def get(self, request, lang, **kwargs):
        if lang in [x[0] for x in LANGUAGES]:
            request.session['django_language'] = lang
            if request.user.is_authenticated():
                request.user.locale = lang
                request.user.save()
        return HttpResponseRedirect(request.META["HTTP_REFERER"])


class ProfileUpdate(UpdateView):
    template_name = 'registration/profile.jinja'
    form_class = ProfileUpdateForm
    success_url = "/accounts/profile/"

    def get_object(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
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

class AccessRequestCreate(TemplateView):
    template_name = 'accessrequest/create.jinja'

    def get_context_data(self):
        request_type = self.request.POST.get("access_type", None)
        if not request_type:
            return {"requested": False}

        u = self.request.user
        if u.is_user and self.REQUEST_TYPE == 'requester':
            return {"status": False, "msg": 'You have already been approved as an Information Requester.'}
        if u.is_volunteer and self.REQUEST_TYPE == 'volunteer':
            return {"status": False, "msg": 'You have already been approved as a Volunteer.'}
        if AccountRequest.objects.filter(user=u, request_type=self.REQUEST_TYPE).count() > 0:
            return {"status": False, "msg": 'You already have an access request pending. Please be patient.'}

        req = AccountRequest(request_type=request_type, user=self.request.user)
        req.save()
        return {"status": True, "requested": request_type}


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


