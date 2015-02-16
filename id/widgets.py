from django import forms
import json

class Select2Field(forms.ChoiceField):
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

    def __init__(self, *args, **kwargs):
        self.placeholder = kwargs.pop('placeholder', None)
        self.ajax_url = kwargs.pop('ajax_url', None)
        self.options = kwargs.pop('options', None)
        self.multiple = kwargs.pop('multiple', None)
        super(Select2Field, self).__init__(*args, **kwargs)
