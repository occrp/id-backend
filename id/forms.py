from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from settings.settings import DEFAULTS
import searchproviders
from id import widgets, constdata, models

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

class CombinedSearchForm(forms.Form):
    query = forms.CharField(
            label="", 
            widget=forms.TextInput(attrs={
                'placeholder': _("Search terms"), 
                'class': 'span8'
            })
        )
    search_providers = forms.MultipleChoiceField(
            label=_("Search Providers"),
            choices=searchproviders.get_providers_names(),
            initial=searchproviders.get_defaults(),
            widget=forms.CheckboxSelectMultiple
        )
    offset = forms.IntegerField(initial=0, widget=forms.HiddenInput)
    limit = forms.IntegerField(initial=DEFAULTS['search']['result_limit'], widget=forms.HiddenInput)


class EntityAjaxSearchForm(forms.Form):
    search_results = forms.MultipleChoiceField()

    # FIXME: Make Ajax URL do something
    #def __init__(self, *args, **kwargs):
    #    super(EntityAjaxSearchForm, self).__init__(*args, **kwargs)
    #    # self.search_results.ajax_url = reverse('search_entities')


# FIXME: This is stupid
class DirectUploadForm(forms.Form):
    key   = forms.HiddenInput()
    redirect_to = forms.HiddenInput()
    file1 = forms.FileField(label='')
    file2 = forms.FileField(label='')
    file3 = forms.FileField(label='')


class UserFilterForm(forms.Form):
    user = forms.ChoiceField(label=_("Customer"))

    # FIXME: Make Ajax URL do something
    def __init__(self, *args, **kwargs):
        super(UserFilterForm, self).__init__(*args, **kwargs)
        self["user"].ajax_url = reverse('select2_all_users')

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        exclude = ('user',)
        model = models.Profile

class ProfileBasicsForm(forms.ModelForm):
    class Meta:
        model = models.Profile
        fields = ("first_name", "last_name", "abbr", "locale", 
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
        fields = ("findings_visible", "is_user", "is_staff", "is_volunteer", "is_superuser")


class ScraperRequestForm(forms.ModelForm):
    class Meta:
        model = models.DatabaseScrapeRequest
    