from django.views.generic import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from id.models import Profile, AccountRequest
from id.forms import ProfileUpdateForm

class ProfileView(DetailView):
    template_name = 'registration/profile_view.jinja'
    model = Profile

class ProfileUpdate(UpdateView):
    template_name = 'registration/profile.jinja'
    model = Profile
    form = ProfileUpdateForm

    def get_object(self, *args, **kwargs):
        return self.request.user.profile

class UserList(ListView):
    model = User
    paginate_by = 50

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

