from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from .models import Feedback

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        exclude = ("timestamp", )
