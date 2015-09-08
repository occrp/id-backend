from django.db import models
from settings.settings import AUTH_USER_MODEL
from id.constdata import *
import re
from core.utils import json_dumps, json_loads
from django.core.urlresolvers import reverse_lazy

notification_channel_format = re.compile("^(([\w\d]+|\*):){4}(([\w\d]+|\*))$")

class Notification(models.Model):
    user            = models.ForeignKey(AUTH_USER_MODEL)
    timestamp       = models.DateTimeField(auto_now_add=True)
    is_seen         = models.BooleanField(default=False)
    text            = models.CharField(max_length=50)
    url_base        = models.CharField(max_length=50, blank=True, null=True)
    url_params      = models.CharField(max_length=200, blank=True, null=True)

    project         = models.CharField(max_length=10, null=True)
    module          = models.CharField(max_length=20, null=True)
    model           = models.CharField(max_length=30, null=True)
    instance        = models.IntegerField(null=True)
    action          = models.CharField(max_length=20, null=True)

    def seen(self):
        self.is_seen = True
        self.save()

    def create(self, user, channel, text, urlname=None, params={}):
        self.apply_components(self.channel_components(channel))
        self.user = user
        self.text = text
        self.url_base = urlname
        self.url_params = json_dumps(params)
        self.save()

    def get_urlparams(self):
        return json_loads(self.url_params)

    def get_url(self):
        return reverse_lazy(self.url_base, kwargs=self.get_urlparams())

    @property
    def channel(self):
        ":".join([self.project, self.module, self.model, self.instance, self.action])
        # = models.CharField(max_length=200)

    def channel_components(self, channel):
        components = ("project", "module", "model", "instance", "action")
        return dict(zip(components, channel.split(":")))

    def apply_components(self, comp):
        for c, v in comp.iteritems():
            setattr(self, c, v)

    def get_icon(self):
        return NOTIFICATION_ICONS.get(self.action, 'other')


class NotificationSubscription(models.Model):
    user            = models.ForeignKey(AUTH_USER_MODEL)
    project         = models.CharField(max_length=10, null=True)
    module          = models.CharField(max_length=20, null=True)
    model           = models.CharField(max_length=30, null=True)
    instance        = models.IntegerField(null=True)
    action          = models.CharField(max_length=20, null=True)
    timestamp       = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('user', 'project', 'module', 'model', 'instance', 'action'), )

    @property
    def channel(self):
        return ":".join([self.project, self.module, self.model, self.instance, self.action])
        # = models.CharField(max_length=200)

    def channel_components(self, channel):
        components = ("project", "module", "model", "instance", "action")
        return dict(zip(components, channel.split(":")))

    def apply_components(self, comp):
        for c, v in comp.iteritems():
            if v == "*":
                setattr(self, c, None)
            else:
                setattr(self, c, v)

    def set_channel(self, channel):
        self.apply_components(self.channel_components(channel))
