from django.forms import Form, ChoiceField, CharField, ModelForm

from .models import DATABASE_COUNTRIES, DATABASE_TYPES, ExternalDatabase


class CountryFilterForm(Form):
    """Filter form for countries."""

    filter = CharField(label="Filter", required=False)
    country = ChoiceField(help_text="", choices=DATABASE_COUNTRIES,
                          required=False)
    db_type = ChoiceField(label="Database type",
                          choices=[('', 'All')] + list(DATABASE_TYPES),
                          required=False)
