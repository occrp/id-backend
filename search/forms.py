from django import forms
from django.utils.translation import ugettext_lazy as _

from settings.settings import DEFAULTS


class CombinedSearchForm(forms.Form):
    query = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={
            'placeholder': _("Search terms"),
            'class': 'span8'
        })
    )
    offset = forms.IntegerField(initial=0, widget=forms.HiddenInput)
    limit = forms.IntegerField(initial=DEFAULTS['search']['result_limit'],
                               widget=forms.HiddenInput)
