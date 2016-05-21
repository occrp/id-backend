from django.conf.urls import patterns, url

from core.auth import perm

from .admin import Feedback, FeedbackThanks

urlpatterns = patterns('',
    url(r'^$',                     perm('any', Feedback), name='feedback'),
    url(r'^thankyou/$',            perm('any', FeedbackThanks), name='feedback_thanks')
)

