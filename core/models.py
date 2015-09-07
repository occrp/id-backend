from django.db import models
from settings.settings import AUTH_USER_MODEL
from id.constdata import *

class Notification(models.Model):
    user            = models.ForeignKey(AUTH_USER_MODEL)
    name            = models.CharField(max_length=200)
    action          = models.IntegerField(choices=NOTIFICATION_ACTIONS, default=0)
    timestamp       = models.DateTimeField(auto_now_add=True)
    is_seen         = models.BooleanField(default=False)
    text            = models.CharField(max_length=50)
    url_base        = models.CharField(max_length=50, blank=True, null=True)
    url_params      = models.CharField(max_length=200, blank=True, null=True)

    def seen(self):
        self.is_seen = True
        self.save()

    def create(self, user, channel, text, urlname=None, params={}, action=NA_NONE):
        self.user = user
        self.channel = channel
        self.action = action
        self.text = text
        self.url_base = urlname
        self.url_params = json_dumps(params)
        self.save()

    def get_urlparams(self):
        return json_loads(self.url_params)

    def get_url(self):
        return reverse_lazy(self.url_base, kwargs=self.get_urlparams())

    def get_icon(self):
        return dict(NOTIFICATION_ICONS).get(self.action, 100000)

class NotificationSubscription(models.Model):
    user            = models.ForeignKey(AUTH_USER_MODEL)
    channel         = models.CharField(max_length=200)
    timestamp       = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('user', 'channel'), )


def notifications_subscribe(user, channel):
    ns = NotificationSubscription(user=user, channel=channel)
    ns.save()

# notify("id:podaci:collection:.{9,19}", "Hello")
