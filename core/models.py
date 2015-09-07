from django.db import models
from settings.settings import AUTH_USER_MODEL
from id.constdata import *
import re

notification_channel_format = re.compile("^(([\w\d]+|\*):)+(([\w\d]+|\*))$")

class Notification(models.Model):
    user            = models.ForeignKey(AUTH_USER_MODEL)
    channel         = models.CharField(max_length=200)
    timestamp       = models.DateTimeField(auto_now_add=True)
    is_seen         = models.BooleanField(default=False)
    text            = models.CharField(max_length=50)
    url_base        = models.CharField(max_length=50, blank=True, null=True)
    url_params      = models.CharField(max_length=200, blank=True, null=True)

    def seen(self):
        self.is_seen = True
        self.save()

    def create(self, user, channel, text, urlname=None, params={}):
        print "Creating a notification on channel '%s'" % channel
        self.user = user
        self.channel = channel
        self.text = text
        self.url_base = urlname
        self.url_params = json_dumps(params)
        self.save()

    def get_urlparams(self):
        return json_loads(self.url_params)

    def get_url(self):
        return reverse_lazy(self.url_base, kwargs=self.get_urlparams())

    @property
    def channel_components(self):
        components = ("project", "module", "model", "instance", "type")
        return dict(zip(components, self.channel.split(":")))

    @property
    def action(self):
        return self.channel_components["action"]

    def get_icon(self):
        return NOTIFICATION_ICONS.get(self.action, 'other')

class NotificationSubscription(models.Model):
    user            = models.ForeignKey(AUTH_USER_MODEL)
    channel         = models.CharField(max_length=200)
    timestamp       = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('user', 'channel'), )

def notification_channels_list():
    return [x.channel for x in Notification.objects.distinct("channel")]
