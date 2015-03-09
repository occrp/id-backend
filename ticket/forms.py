from django import forms
from django.utils.translation import ugettext_lazy as _

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

class RequestChargeForm(forms.Form):
    """
    Add a charge to a ticket!
    """
    comment = forms.CharField(label=_("Comment to Requester"), widget=forms.Textarea)
    item = forms.CharField(label=_("Item"), required=True)
    cost = forms.DecimalField(label=_("Cost (USD)"), required=True)
    cost_original_currency = forms.DecimalField(
        label=_("Cost (Original Currency)"))
    original_currency = forms.ChoiceField(
        label=_("Original Currency Name"),
        choices=constants.CURRENCIES,
        initial="EUR")

class TicketTypeForm(forms.Form):
    ticket_type = forms.ChoiceField(
        label=_('Research Goal'),
        choices=constants.TICKET_TYPES,
        required=True,
        widget=forms.RadioSelect)


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
    class Meta(TicketForm.Meta):
        model = models.PersonTicket
        fields = ('name', 'aliases', 'background', 'biography',
                  'family', 'business_activities', 'dob', 'birthplace',
                  'initial_information', 'location', 'deadline',
                  'sensitive')
        field_args = {
            'aliases': {'description': _("Other names they are known by")},
            'background': {
                'placeholder': _('What do you know so far?'),
                'css_class': 'span8',
            },
            'biography': {'css_class': 'span8'},
            'business_activities': {'css_class': 'span8'},
            'initial_information': {
                'placeholder': _('Any information you already have.'),
                'css_class': 'span8',
            },
            'location': {'description': _('Where are you researching?')},
        }
        ajax_validation_url = "/_validation/request/"
    Meta.field_args.update(TicketForm.Meta.field_args)

    def __init__(self, *args, **kwargs):
        super(PersonTicketForm, self).__init__(*args, **kwargs)
        self.fields['deadline'].widget.attrs.update({'class': 'datepicker'})
        self.fields['dob'].widget.attrs.update({'class': 'datepicker'})


class CompanyTicketForm(TicketForm):
    class Meta(TicketForm.Meta):
        model = models.CompanyTicket
        fields = ('name', 'country', 'background', 'sources',
                  'story', 'connections', 'deadline', 'sensitive')
        field_args = {
            'country': {'choices': constants.COUNTRIES},
            'background': {
                'placeholder': _('What do you know so far?'),
                'css_class': 'span8',
            },
            'story': {
                'placeholder': _('What story are you working on?'),
                'css_class': 'span8'
            },
            'sources': {
                'placeholder': _('What sources do you have so far?'),
                'css_class': 'span8',
            },
        }
        ajax_validation_url = "/_validation/request/"
    Meta.field_args.update(TicketForm.Meta.field_args)

    def __init__(self, *args, **kwargs):
        super(CompanyTicketForm, self).__init__(*args, **kwargs)
        self.fields['deadline'].widget.attrs.update({'class': 'datepicker'})


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
        self.fields['deadline'].widget.attrs.update({'class': 'datepicker'})


class RequestCancelForm(forms.Form):
    reason = forms.CharField(label=_("Reason"), widget=forms.Textarea)

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
                    "placeholder":_("Add a comment, visible to the person making "
                                    "this request and the researcher answering it."),
                    "class": "span9"
                }
            )
        }
