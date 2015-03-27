from django.http import HttpResponseRedirect
from django.views.generic import *
from django.contrib.auth.decorators import login_required
#from django.contrib.auth.models import User
from django.contrib.auth import get_user_model # as per https://docs.djangoproject.com/en/dev/topics/auth/customizing/#referencing-the-user-model
from settings.settings import LANGUAGES
from registration.signals import user_registered

from id.models import Profile, AccountRequest
from id.forms import ProfileUpdateForm, ProfileBasicsForm, ProfileDetailsForm, ProfileAdminForm


class ProfileSetLanguage(TemplateView):
    template_name = 'registration/profile.jinja'

    def get(self, request, lang, **kwargs):
        if lang in [x[0] for x in LANGUAGES]:
            request.session['django_language'] = lang
            if request.user.is_authenticated():
                request.user.profile.locale = lang
                request.user.profile.save()
        return HttpResponseRedirect(request.META["HTTP_REFERER"])


class ProfileUpdate(UpdateView):
    template_name = 'registration/profile.jinja'
    form_class = ProfileUpdateForm
    success_url = "/accounts/profile/"

    def get_object(self, *args, **kwargs):
        if kwargs.has_key("pk"):
            return get_user_model().objects.get(id=kwargs["pk"]).profile
        elif kwargs.has_key("username"):
            return get_user_model().objects.get(username=kwargs["username"]).profile
        return self.request.user.profile

    def get_context_data(self, form):
        obj = self.get_object()
        ctx = super(ProfileUpdate, self).get_context_data()
        ctx = {
            "editing_self": obj == self.request.user.profile
        }
        print "Request method: ", self.request.method
        if self.request.method == "POST":
            ctx["form"] = ProfileUpdateForm(self.request.POST, instance=obj)
            if ctx["form"].is_valid():
                print "Saving form. Form: ", ctx["form"]
                obj = ctx["form"].save()
            else:
                print ctx["form"].errors
            ctx["form_basics"] = ProfileBasicsForm(self.request.POST, instance=obj)
            ctx["form_details"] = ProfileDetailsForm(self.request.POST, instance=obj)
            if obj.is_superuser:
                ctx["form_admin"] = ProfileAdminForm(self.request.POST, instance=obj)
        else:
            ctx["form"] = ProfileUpdateForm(instance=obj)
            ctx["form_basics"] = ProfileBasicsForm(instance=obj)
            ctx["form_details"] = ProfileDetailsForm(instance=obj)
            if obj.is_superuser:
                ctx["form_admin"] = ProfileAdminForm(instance=obj)
        return ctx

class UserList(ListView):
    model = get_user_model()
    paginate_by = 50
    template_name = 'auth/user_list.jinja'

class AccountRequestHome(TemplateView):
    template_name = 'request_account_home.jinja'

    def message(self, where, message):
        self.add_message(message)
        self.redirect_to(where)
        return True

    def fallback_response(self):
        if not self.user:
            return False
        if self.profile.is_user:
            return self.message(
                'request_list',
                'You have already been approved as an Information Requester.')
        if self.profile.is_volunteer:
            return self.message(
                'request_list',
                'You have already been approved as a Volunteer.')
        if models.AccountRequest.pending_for(self.user):
            return self.message(
                'home',
                'You already have a request for an account pending.'
                ' Please be patient.')

class AccountRequestList(ListView):
    template_name = 'id/accountrequest_list.jinja'
    model = AccountRequest

class AccountRequest(AccountRequestHome):
    # form_class = forms.modelform_factory(forms.AccountRequestForm)
    template_name = 'request_account.jinja'

    @login_required
    def _get(self):
        if self.fallback_response():
            return
        form = self.form_class(email=self.profile.email)
        return (self.fallback_response()
                or self.render_response(self.template_name, form=form))

    @login_required
    def _post(self):
        f = self.form_class(self.request.POST)
        f.email.data = self.profile.email

        if not f.validate():
            logging.info("Fail to validate for unknown reason!")
            return self.render_response(self.template_name, form=f)

        account_request = f.save(parent=ndb.Key('Entity', 'accountrequest'),
                                 commit=False)
        account_request.user_profile = self.profile.key
        account_request.put()
        account_request.notify_received()
        self.add_message(_('Request submitted. Our staff will evaluate and '
                           'respond to your request.'), 'success')
        self.redirect_to('home')


class AccountVolunteer(AccountRequest):
    # form_class = forms.modelform_factory(forms.AccountVolunteerForm)
    template_name = 'accountrequest/volunteer_account.jinja'

