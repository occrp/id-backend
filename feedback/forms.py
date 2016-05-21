from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

import id.models

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = id.models.Feedback
        exclude = ("timestamp", )
