import re
import math
from captcha.fields import CaptchaField

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model

from . import models


class ProfileRegistrationForm(forms.Form):
    """Form for registering a new user account."""

    first_name = forms.CharField(
            widget=forms.TextInput(),
            label=_('First name'))
    last_name = forms.CharField(
            widget=forms.TextInput(),
            label=_('Last/family name'))
    organization = forms.CharField(
            widget=forms.TextInput(),
            label=_('Organization'),
            help_text=_('Your affiliation with a news or research organisation, or freelance.'))
    email = forms.EmailField(
            widget=forms.TextInput(),
            label=_('E-mail Address'),
            help_text=_('You will receive a confirmation and use this address to sign in.'))
    password1 = forms.CharField(
            widget=forms.PasswordInput(render_value=False),
            label=_('Password'))
    password2 = forms.CharField(
            widget=forms.PasswordInput(render_value=False),
            label=_('Password confirmation'))
    """
    Captcha, because why not
    """
    captcha = CaptchaField()

    def clean_email(self):
        """Validate that the email is valid and is not already in use."""
        try:
            get_user_model().objects.get(email=self.cleaned_data['email'])
        except get_user_model().DoesNotExist:
            return self.cleaned_data['email']
        msg = _(u'A user with this e-mail address has already registered.')
        raise forms.ValidationError(msg)

    def clean_password1(self):
        """Validate that the password is good enough.

        We only have to do it for password1, as we're checking elsewhere
        if password1 and password2 match
        """
        score = 0
        password = self.cleaned_data['password1']

        # small letters
        if re.search('[a-z]+', password):
            score += 26
        # capital letters
        if re.search('[A-Z]+', password):
            score += 26
        # digits
        if re.search('[0-9]+', password):
            score += 10
        # anything else?
        if re.search('^[a-zA-Z0-9]+$', password) is None:
            score += 46

        # math!
        if math.log(score**len(password), 2) < 50:
            raise forms.ValidationError(_(u'Please provide a longer password'))

        # we're done here
        return self.cleaned_data['password1']

    def clean(self):
        """Verify that the values entered into the two password fields match.

        Note that an error here will end up in ``non_field_errors()`` because
        it doesn't apply to a single field.
        """
        data = self.cleaned_data
        if 'password1' in data and 'password2' in data:
            if data['password1'] != data['password2']:
                msg = _(u'You must type the same password each time')
                raise forms.ValidationError(msg)
        return self.cleaned_data

    def save(self, profile_callback=None):
        new_user = get_user_model().objects.create_user(
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password1'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            organization=self.cleaned_data['organization'])
        return new_user


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = models.Profile
        fields = ("first_name", "last_name", "locale",
                  "country", "phone_number", "organization",)
        exclude = ('user', 'password', 'last_login', 'email', 'date_joined',
                   "network", "is_staff", "is_superuser", "is_active")
