from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from id import constdata, models
from django.contrib.auth import get_user_model
import re
import math


class CountryFilterForm(forms.Form):
    """
    Filter form for countries.

    Expects 'records' kwarg which should be a collection of external databases
    from which to extract the country options from.

    We use '---' as a divider
    """
    country = forms.ChoiceField(
                label="", #_("Country"),
                help_text="",
                choices=constdata.DATABASE_COUNTRIES,
              )


class UserFilterForm(forms.Form):
    user = forms.ChoiceField(label=_("Customer"))

    # FIXME: Make Ajax URL do something
    def __init__(self, *args, **kwargs):
        super(UserFilterForm, self).__init__(*args, **kwargs)
        self["user"].ajax_url = reverse('select2_all_users')


class ProfileRegistrationForm(forms.Form):
    """
    Form for registering a new user account.
    """
    email = forms.EmailField(
            widget=forms.TextInput(attrs=dict(attrs={ 'class': 'required' }, maxlength=254)),
            label=_('E-mail Address'))
    password1 = forms.CharField(
            widget=forms.PasswordInput(attrs={ 'class': 'required' }, render_value=False),
            label=_('Password'))
    password2 = forms.CharField(
            widget=forms.PasswordInput(attrs={ 'class': 'required' }, render_value=False),
            label=_('Password confirmation'))

    def clean_email(self):
        """
        Validate that the email is valid and is not already
        in use.

        """
        try:
            user = get_user_model().objects.get(email=self.cleaned_data['email'])
        except get_user_model().DoesNotExist:
            return self.cleaned_data['email']
        raise forms.ValidationError(_(u'A user with this e-mail address has already registered.'))

    def clean_password1(self):
        """
        Validate that the password is good enough
        we only have to do it for password1, as we're checking elsewhere if password1 and password2 match

        """
        score = 0

        # small letters
        if re.search('[a-z]+', self.cleaned_data['password1']):
            score += 26
        # capital letters
        if re.search('[A-Z]+', self.cleaned_data['password1']):
            score += 26
        # digits
        if re.search('[0-9]+', self.cleaned_data['password1']):
            score += 10
        # anything else?
        if re.search('^[a-zA-Z0-9]+$', self.cleaned_data['password1']) == None:
            score += 46

        # math!
        if math.log(score**len(self.cleaned_data['password1']), 2) < 50:
            raise forms.ValidationError(_(u'Please provide a longer password'))

        # we're done here
        return self.cleaned_data['password1']

    def clean(self):
        """
        Verify that the values entered into the two password fields
        match. Note that an error here will end up in
        ``non_field_errors()`` because it doesn't apply to a single
        field.

        """
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_(u'You must type the same password each time'))
        return self.cleaned_data

    def save(self, profile_callback=None):
        new_user = get_user_model().objects.create_user(
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password1'])
        return new_user


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        exclude = ('user',)
        model = models.Profile


class ProfileBasicsForm(forms.ModelForm):
    class Meta:
        model = models.Profile
        fields = ("first_name", "last_name", "locale",
                  "country", "network")


class ProfileDetailsForm(forms.ModelForm):
    class Meta:
        model = models.Profile
        fields = ("phone_number", "organization_membership",
                  "address",
                  "city", "province", "postal_code", "industry",
                  "media", "circulation", "title", "interests",
                  "expertise", "languages", "availability",
                  "databases", "conflicts")


class ProfileAdminForm(forms.ModelForm):
    class Meta:
        model = models.Profile
        fields = ("findings_visible", "is_user", "is_staff", "is_volunteer", "is_superuser", "is_active")


class ScraperRequestForm(forms.ModelForm):
    class Meta:
        model = models.DatabaseScrapeRequest


from captcha.fields import CaptchaField

class FeedbackForm(forms.ModelForm):
    if not get_user_model()().is_authenticated():
        captcha = CaptchaField()
    class Meta:
        model = models.Feedback