from django.forms import Form, ChoiceField, CharField, ModelForm

from .models import DATABASE_COUNTRIES, DATABASE_TYPES, ExternalDatabase


class CountryFilterForm(Form):
    """ Filter form for countries. """
    filter = CharField(label="Filter")
    country = ChoiceField(help_text="", choices=DATABASE_COUNTRIES)
    db_type = ChoiceField(label="Database type",
                          choices=[('', 'All')]+list(DATABASE_TYPES))


class ExternalDatabaseForm(ModelForm):
    class Meta:
        model = ExternalDatabase
        fields = ('agency', 'db_type', 'country', 'paid',
                  'registration_required', 'government_db', 'url', 'notes',
                  'blog_post', 'video_url')
