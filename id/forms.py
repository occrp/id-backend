from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from . import models

class ScraperRequestForm(forms.ModelForm):
    class Meta:
        model = models.DatabaseScrapeRequest
        exclude = tuple()


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = models.Feedback
        exclude = ("timestamp", )
