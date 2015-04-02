from django import forms
#from django.contrib.auth.models import User
from django.contrib.auth import get_user_model # as per https://docs.djangoproject.com/en/dev/topics/auth/customizing/#referencing-the-user-model
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from django_select2 import *

import core.widgets
import core.utils

from ticket import constants
from ticket import models

class DirectUploadForm(forms.Form):
    key = forms.HiddenInput()
    redirect_to = forms.HiddenInput()
    file1 = forms.FileField(label='')
    file2 = forms.FileField(label='')
    file3 = forms.FileField(label='')

class TicketPaidForm(forms.Form):
    """
    Update a ticket with it's payment status (from within the ticket).
    """
    comment = forms.CharField(
        label=_("Comment"), 
        widget=forms.Textarea)
    paid_status = forms.ChoiceField(
        label=_("Paid Status"),
        help_text=_("Marking as paid will reconcile any open charges with the request."),
        choices=constants.PAID_STATUS,
        required=True,
        widget=forms.RadioSelect)

class RequestChargeForm(forms.ModelForm):
    """
    Add a charge to a ticket!
    """
    class Meta:
        model = models.TicketCharge
        exclude = ['ticket', 'user']
        widgets = {
            'cost_original_currency': forms.Select(choices=constants.CURRENCIES)
        }
        
    #comment = forms.CharField(label=_("Comment to Requester"), widget=forms.Textarea)
    #item = forms.CharField(label=_("Item"), required=True)
    #cost = forms.DecimalField(label=_("Cost (USD)"), required=True)
    # cost_original_currency = forms.DecimalField(
    #    label=_("Cost (Original Currency)"))
    #original_currency = forms.ChoiceField(
    #    label=_("Original Currency Name"),
    #    choices=constants.CURRENCIES,
    #    initial="EUR")

class TicketTypeForm(forms.Form):
    ticket_type = forms.ChoiceField(
        label=_('Research Goal'),
        choices=constants.TICKET_TYPES,
        required=True,
        widget=forms.RadioSelect)

    def __init__(self, *args, **kwargs):
        if 'ticket_type' in kwargs:
            self.ticket_type = kwargs.pop('ticket_type')

        super(TicketTypeForm, self).__init__(*args, **kwargs)
        self.prefix = 'ticket_type'


class TicketForm(forms.ModelForm):
    class Meta:
        field_args = {
            'sensitive': {
                'description': _('This is highly sensitive, do not let '
                                 'volunteer research librarians see this '
                                 'request.')
            }
        }

class PersonTicketForm(TicketForm):

    def clean_family(self):
        data = self.cleaned_data['family']
        return data.strip()

    def clean_aliases(self):
        data = self.cleaned_data['aliases']
        return data.strip()

    class Meta(TicketForm.Meta):
        model = models.PersonTicket
        fields = ('name', 'aliases', 'background', 'biography',
                  'family', 'business_activities', 'dob', 'birthplace',
                  'initial_information', 'location', 'deadline',
                  'sensitive')
        # field_args = {
        #     'aliases': {'description': _("Other names they are known by")},
        #     'background': {
        #         'placeholder': _('What do you know so far?'),
        #         'css_class': 'span8',
        #     },
        #     'biography': {'css_class': 'span8'},
        #     'business_activities': {'css_class': 'span8'},
        #     'initial_information': {
        #         'placeholder': _('Any information you already have.'),
        #         'css_class': 'span8',
        #     },
        #     'location': {'description': _('Where are you researching?')},
        # }
        # ajax_validation_url = "/_validation/request/"
    Meta.field_args.update(TicketForm.Meta.field_args)

    def __init__(self, *args, **kwargs):
        super(PersonTicketForm, self).__init__(*args, **kwargs)
        self.fields['deadline'].widget.attrs.update({'class': 'datepicker deadline'})
        self.fields['dob'].widget.attrs.update({'class': 'datepicker dob'})
        self.fields['background'].widget.attrs.update({'class': 'span8', 'placeholder': _('What do you know so far?'), 'rows': '6'})
        self.fields['biography'].widget.attrs.update({'class': 'span8', 'rows': '6'})
        self.fields['business_activities'].widget.attrs.update({'class': 'span8', 'rows': '6'})
        self.fields['initial_information'].widget.attrs.update({'class': 'span8', 'placeholder': _('Any information you already have.'), 'rows': '6'})
        self.fields['location'].widget.attrs.update({'placeholder': _('Where are you researching?')})
        self.prefix = "person"


class CompanyTicketForm(TicketForm):

    def clean_connections(self):
        data = self.cleaned_data['connections']
        return data.strip()

    class Meta(TicketForm.Meta):
        model = models.CompanyTicket
        fields = ('name', 'country', 'background', 'sources',
                  'story', 'connections', 'deadline', 'sensitive')
        # field_args = {
        #     'country': {'choices': constants.COUNTRIES},
        #     'background': {
        #         'placeholder': _('What do you know so far?'),
        #         'css_class': 'span8',
        #     },
        #     'story': {
        #         'placeholder': _('What story are you working on?'),
        #         'css_class': 'span8'
        #     },
        #     'sources': {
        #         'placeholder': _('What sources do you have so far?'),
        #         'css_class': 'span8',
        #     },
        # }
        # ajax_validation_url = "/_validation/request/"
    Meta.field_args.update(TicketForm.Meta.field_args)

    def __init__(self, *args, **kwargs):
        super(CompanyTicketForm, self).__init__(*args, **kwargs)
        self.fields['deadline'].widget.attrs.update({'class': 'datepicker deadline'})
        self.fields['background'].widget.attrs.update({'class': 'span8', 'placeholder': _('What do you know so far?'), 'rows': '6'})
        self.fields['story'].widget.attrs.update({'class': 'span8', 'placeholder': _('What story are you working on?'), 'rows': '6'})
        self.fields['sources'].widget.attrs.update({'class': 'span8', 'placeholder': _('What sources do you have so far?'), 'rows': '6'})
        self.prefix = "company"

class OtherTicketForm(TicketForm):
    class Meta(TicketForm.Meta):
        model = models.OtherTicket
        fields = ('question', 'deadline', 'sensitive')
        field_args = {
            'question': {
                'css_class': 'span8',
            }
        }
        ajax_validation_url = "/_validation/request/"
    Meta.field_args.update(TicketForm.Meta.field_args)

    def __init__(self, *args, **kwargs):
        super(OtherTicketForm, self).__init__(*args, **kwargs)
        self.fields['deadline'].widget.attrs.update({'class': 'datepicker deadline'})
        self.fields['question'].widget.attrs.update({'class': 'span8', 'rows': '6'})
        self.prefix = "other"


# class MultiResponderChoices(Select2MultipleChoiceField):
#     choices = get_user_model().objects.all().filter(Q(profile__is_superuser=1) | Q(profile__is_staff=1))

class TicketAdminSettingsForm(forms.ModelForm):
    responders = Select2MultipleChoiceField(label=_("Staff Responders"), required=False)
    volunteers = Select2MultipleChoiceField(label=_("Volunteer Responders"), required=False)
    redirect = forms.CharField(required=False, initial="default", widget=forms.HiddenInput)

    class Meta:
        model = models.Ticket
        fields = ['responders', 'volunteers', 'requester_type', 'findings_visible', 'is_for_profit', 'is_public']
        widgets = {
            'requester_type': forms.RadioSelect()
        }

    def __init__(self, *args, **kwargs):

        super(TicketAdminSettingsForm, self).__init__(*args, **kwargs)
        self.fields['responders'].choices = core.utils.convert_group_to_select2field_choices(
                                                get_user_model().objects.all().filter(Q(is_superuser=1) | Q(is_staff=1)))
        self.fields['volunteers'].choices = core.utils.convert_group_to_select2field_choices(
                                                get_user_model().objects.all().filter(Q(is_volunteer=1)))
        self.fields['requester_type'].widget.attrs.update({'choices': constants.REQUESTER_TYPES})


class TicketCancelForm(forms.ModelForm):
    reason = forms.CharField(label=_("Reason"), widget=forms.Textarea(attrs={'rows': 6}))

    class Meta:
        model = models.Ticket
        fields = ['reason']

class TicketEmptyForm(forms.ModelForm):
    # this is for when no field validation is needed, but a ticket still
    # needs to be actioned by a POST method

    class Meta:
        model = models.Ticket
        fields = []


class RequestFlagForm(forms.Form):
    comment = forms.CharField(
        label=_("Comment"),
        widget=forms.Textarea,
        required=True)


class CommentForm(forms.ModelForm):
    class Meta:
        model = models.TicketUpdate
        fields = ["comment"]
        widgets = {
            "author": forms.HiddenInput(),
            "ticket": forms.HiddenInput(),
            "comment": forms.Textarea(
                attrs={
                    "placeholder": _("Add a comment, visible to the person making "
                                     "this request and the researcher answering it."),
                    "class": "span9"
                }
            )
        }


class BudgetForm(forms.ModelForm):
    class Meta:
        model = models.Budget