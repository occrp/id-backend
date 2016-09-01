import re
import logging

from django.db import models
from settings.settings import AUTH_USER_MODEL

from django.core.urlresolvers import reverse

from .utils import json_dumps, json_loads

log = logging.getLogger(__name__)

notification_channel_format = re.compile("^(([\w\d]+|\*):){4}(([\w\d]+|\*))$")

NOTIFICATION_ICONS = {
    "none": 'bell-o',
    "add": 'plus-square',
    "edit": 'pencil-square',
    "delete": 'minus-square',
    "update": 'edit',
    "share": 'share-alt-square',
    "other": 'bomb'
}


def channel_components(channel):
    components = ("project", "module", "model", "instance", "action")
    return dict(zip(components, [None if x == '*' else x for x in channel.split(":")]))


def all_known_channels():
    # FIXME: Ugly monster of a function.
    results = []
    for project in Notification.objects.values('project').distinct():
        for module in Notification.objects.filter(project=project['project']).values('module').distinct():
            for model in Notification.objects.filter(project=project['project'], module=module['module']).order_by().values('model').distinct():
                for action in Notification.objects.filter(
                            project=project['project'],
                            module=module['module'],
                            model=model['model']).order_by().values('action').distinct():
                    results.append("%s:%s:%s:*:%s" % (project['project'], module['module'], model['model'], action['action']))
    return results


class Notification(models.Model):
    user            = models.ForeignKey(AUTH_USER_MODEL)
    timestamp       = models.DateTimeField(auto_now_add=True)
    is_seen         = models.BooleanField(default=False)
    text            = models.CharField(max_length=10000)
    url_base        = models.CharField(max_length=50, blank=True, null=True)
    url_params      = models.CharField(max_length=2000, blank=True, null=True)
    url             = models.URLField(blank=True, null=True)

    project         = models.CharField(max_length=255, null=True)
    module          = models.CharField(max_length=255, null=True)
    model           = models.CharField(max_length=255, null=True)
    instance        = models.IntegerField(null=True)
    action          = models.CharField(max_length=255, null=True)

    class Meta:
        ordering = ['-timestamp']

    def seen(self):
        self.is_seen = True
        self.save()

    def create(self, user, channel, text, urlname=None, params={}, url=None):
        self.apply_components(channel_components(channel))
        self.user = user
        if text is not None:
            text = text[:10000]
        self.text = text
        self.url_base = urlname
        self.url_params = json_dumps(params)
        self.url = url
        self.save()

        message = """
    Dear %(user)s, you have received a notification from Investigative Dashboard. It reads:

        %(message)s

    Regards, ID
        """ % {"user": self.user, "message": self.text}
        self.user.email_user("Investigative Dashboard just sent you a notification", message)

    def get_urlparams(self):
        return json_loads(self.url_params)

    def get_url(self):
        if self.url_base:
            try:
                return reverse(self.url_base, kwargs=self.get_urlparams())
            except Exception as ex:
                log.exception(ex)
                return None
        elif self.url:
            return self.url
        return None

    @property
    def channel(self):
        return ":".join([self.project, self.module, self.model,
                         str(self.instance), self.action])

    def apply_components(self, comp):
        for c, v in comp.iteritems():
            setattr(self, c, v)

    def get_icon(self):
        return NOTIFICATION_ICONS.get(self.action, 'bomb')


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

    def __unicode__(self):
        return self.channel

    @property
    def channel(self):
        return ":".join([unicode(x) if x else '*' for x in
                         [self.project, self.module, self.model,
                          self.instance, self.action]])
        # = models.CharField(max_length=200)

    def apply_components(self, comp):
        for c, v in comp.iteritems():
            if v == "*":
                setattr(self, c, None)
            else:
                setattr(self, c, v)

    def set_channel(self, channel):
        self.apply_components(channel_components(channel))
