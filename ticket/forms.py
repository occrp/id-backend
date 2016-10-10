from django import forms
from django.utils.translation import ugettext_lazy as _
from django_select2.forms import Select2Widget

from core.countries import CURRENCIES

from . import constants
from . import models


class TicketPaidForm(forms.Form):
    """Update a ticket with it's payment status (from within the ticket)."""

    comment = forms.CharField(
        label=_("Comment"),
        widget=forms.Textarea)
    paid_status = forms.ChoiceField(
        label=_("Paid Status"),
        help_text=_("Marking as paid will reconcile any open charges with the request."),
        choices=constants.PAID_STATUS,
        required=True,
        widget=forms.RadioSelect)

    def __init__(self, *args, **kwargs):
        kwargs.pop('instance', None)

        super(TicketPaidForm, self).__init__(*args, **kwargs)


class RequestChargeForm(forms.ModelForm):
    """Add a charge to a ticket."""

    class Meta:
        model = models.TicketCharge
        exclude = ['ticket', 'user', 'created']
        widgets = {
            'original_currency': Select2Widget(choices=CURRENCIES),
        }

    def __init__(self, *args, **kwargs):
        super(RequestChargeForm, self).__init__(*args, **kwargs)
        self.fields['reconciled_date'].widget.attrs.update({'class': 'datepicker'})


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
                                 'research librarians see this request.')
            }
        }


class PersonTicketForm(TicketForm):

    class Meta(TicketForm.Meta):
        model = models.PersonTicket
        fields = ('name', 'surname', 'aliases', 'dob', 'family',
                  'business_activities', 'initial_information', 'background',
                  'deadline', 'sensitive', 'whysensitive')

    Meta.field_args.update(TicketForm.Meta.field_args)

    def __init__(self, *args, **kwargs):
        super(PersonTicketForm, self).__init__(*args, **kwargs)
        self.fields['deadline'].widget.attrs.update({'class': 'datepicker deadline'})
        self.fields['dob'].widget.attrs.update({'class': 'datepicker dob'})
        self.fields['background'].widget.attrs.update({'class': 'span8', 'placeholder': _('What do you know so far?'), 'rows': '6'})
        self.fields['family'].widget.attrs.update({'class': 'span8', 'placeholder': _('Known family relationships.'), 'rows': '2'})
        self.fields['aliases'].widget.attrs.update({'class': 'span8', 'placeholder': _('Other spellings, or cover names.'), 'rows': '2'})
        # self.fields['biography'].widget.attrs.update({'class': 'span8', 'rows': '6'})
        self.fields['business_activities'].widget.attrs.update({'class': 'span8', 'rows': '6'})
        self.fields['initial_information'].widget.attrs.update({'class': 'span8', 'placeholder': _('Any information you already have.'), 'rows': '6'})
        # self.fields['location'].widget.attrs.update({'placeholder': _('Where are you researching?')})
        self.prefix = "person"


class CompanyTicketForm(TicketForm):

    def clean_connections(self):
        data = self.cleaned_data['connections']
        return data.strip()

    class Meta(TicketForm.Meta):
        model = models.CompanyTicket
        fields = ('name', 'country', 'background', 'sources',
                  'connections', 'deadline', 'sensitive', 'whysensitive')

    Meta.field_args.update(TicketForm.Meta.field_args)

    def __init__(self, *args, **kwargs):
        super(CompanyTicketForm, self).__init__(*args, **kwargs)
        self.fields['deadline'].widget.attrs.update({'class': 'datepicker deadline'})
        self.fields['background'].widget.attrs.update({'class': 'span8', 'placeholder': _('What do you know so far?'), 'rows': '6'})
        # self.fields['story'].widget.attrs.update({'class': 'span8', 'placeholder': _('What story are you working on?'), 'rows': '6'})
        self.fields['sources'].widget.attrs.update({'class': 'span8', 'placeholder': _('What sources do you have so far?'), 'rows': '6'})
        self.prefix = "company"


class OtherTicketForm(TicketForm):
    class Meta(TicketForm.Meta):
        model = models.OtherTicket
        fields = ('question', 'deadline', 'sensitive', 'whysensitive')
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


class TicketAdminSettingsForm(forms.ModelForm):
    redirect = forms.CharField(required=False, initial="default",
                               widget=forms.HiddenInput)

    class Meta:
        model = models.Ticket
        fields = ['requester_type', 'findings_visible',
                  'is_for_profit', 'is_public']
        widgets = {
            'requester_type': forms.RadioSelect()
        }

    def __init__(self, *args, **kwargs):
        super(TicketAdminSettingsForm, self).__init__(*args, **kwargs)
        self.fields['requester_type'].widget.attrs.update({
            'choices': constants.REQUESTER_TYPES
        })


class TicketCancelForm(forms.ModelForm):
    reason = forms.CharField(label=_("Reason"),
                             widget=forms.Textarea(attrs={'rows': 6}))

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
        fields = ('name', 'description')
