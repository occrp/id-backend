from django.forms import Form, ChoiceField

from databases.models import DATABASE_COUNTRIES


class CountryFilterForm(Form):
    """ Filter form for countries. """
    country = ChoiceField(label="", help_text="", choices=DATABASE_COUNTRIES)
