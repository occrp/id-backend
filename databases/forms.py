from django.forms import Form, ChoiceField, CharField

from databases.models import DATABASE_COUNTRIES, DATABASE_TYPES


class CountryFilterForm(Form):
    """ Filter form for countries. """
    filter = CharField(label="Filter")
    country = ChoiceField(help_text="", choices=DATABASE_COUNTRIES)
    db_type = ChoiceField(label="Database type", choices=[('','All')]+list(DATABASE_TYPES))
