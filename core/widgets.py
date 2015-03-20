from django import forms
import json

class Select2Field(forms.widgets.SelectMultiple):
    """
    Creates an AJAX Driven Select2 Widget.  For a non-ajax driven widget, use
    a normal SelectField.

    :params

    multiple -- Whether or not the user can select multiple items.
    placeholder -- The text to display on this widget if no info is entered.
    ajax_url -- The AJAX endpoint for data for this select2 field.
    options -- hard coded options list, overrides any ajax_url set.
    """

    attrs = {}
    placeholder = None
    ajax_url = None
    options = {}

    def __init__(self, *args, **kwargs):
        self.attrs['placeholder'] = kwargs.pop('placeholder', None)
        self.attrs['ajax_url'] = kwargs.pop('ajax_url', None)
        self.attrs['options'] = kwargs.pop('options', None)
        self.attrs['multiple'] = kwargs.pop('multiple', None)
        self.attrs['value'] = kwargs.pop('value', None)
        self.attrs['data_text'] = kwargs.pop('data_text', None)
        super(Select2Field, self).__init__(*args, **kwargs)
