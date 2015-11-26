from django.db import models
from settings.settings import AUTH_USER_MODEL
import re
import logging
from core.utils import json_dumps, json_loads
from django.core.urlresolvers import reverse_lazy, reverse
from id.constdata import NOTIFICATION_ICONS

logger = logging.getLogger(__name__)

notification_channel_format = re.compile("^(([\w\d]+|\*):){4}(([\w\d]+|\*))$")

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
    text            = models.CharField(max_length=200)
    url_base        = models.CharField(max_length=50, blank=True, null=True)
    url_params      = models.CharField(max_length=200, blank=True, null=True)
    url             = models.URLField(blank=True, null=True)

    project         = models.CharField(max_length=10, null=True)
    module          = models.CharField(max_length=20, null=True)
    model           = models.CharField(max_length=30, null=True)
    instance        = models.IntegerField(null=True)
    action          = models.CharField(max_length=20, null=True)

    class Meta:
        ordering = ['-timestamp']

    def seen(self):
        self.is_seen = True
        self.save()

    def create(self, user, channel, text, urlname=None, params={}, url=None):
        self.apply_components(channel_components(channel))
        self.user = user
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
            except Exception, e:
                logger.debug("Failed to convert url name '%s' with kwargs %s.", self.url_base, self.url_params)
                return None
        elif self.url:
            return self.url
        return None

    @property
    def channel(self):
        return ":".join([self.project, self.module, self.model, str(self.instance), self.action])

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
        return ":".join([unicode(x) if x else '*' for x in [self.project, self.module, self.model, self.instance, self.action]])
        # = models.CharField(max_length=200)

    def apply_components(self, comp):
        for c, v in comp.iteritems():
            if v == "*":
                setattr(self, c, None)
            else:
                setattr(self, c, v)

    def set_channel(self, channel):
        self.apply_components(channel_components(channel))


class AuditLog(models.Model):
    user         = models.ForeignKey(AUTH_USER_MODEL, null=True)
    level        = models.IntegerField()
    module       = models.CharField(max_length=100)
    filename     = models.CharField(max_length=100)
    lineno       = models.IntegerField()
    funcname     = models.CharField(max_length=100)
    message      = models.TextField(null=True, blank=True)
    excinfo      = models.TextField(null=True, blank=True)
    exctext      = models.TextField(null=True, blank=True)
    process      = models.IntegerField()
    thread       = models.IntegerField()
    ip           = models.IPAddressField(blank=True, null=True)
    timestamp    = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"[%s/%d] %s:%d@%d-%d: %s" % (self.timestamp, self.level, self.filename, self.lineno, self.process, self.thread, self.message)
