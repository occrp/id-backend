from django.forms import Form, ChoiceField

from databases.fixtures import DATABASE_COUNTRIES


class CountryFilterForm(Form):
    """
    Filter form for countries.

    Expects 'records' kwarg which should be a collection of external databases
    from which to extract the country options from.

    We use '---' as a divider
    """
    country = ChoiceField(label="", help_text="", choices=DATABASE_COUNTRIES)
