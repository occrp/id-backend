from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.mixins import DisplayMixin
from settings.settings import AUTH_USER_MODEL

REQUEST_TYPES = (
    ('requester', _('Information Requester')),
    ('volunteer', _('Volunteer'))
)


######## Account management ############
class AccountRequest(models.Model, DisplayMixin):
    request_type = models.CharField(blank=False, max_length=64, choices=REQUEST_TYPES)
    user = models.ForeignKey(AUTH_USER_MODEL, blank=False)
    approved = models.NullBooleanField(default=None, blank=True, null=True, verbose_name=_('Approved'))
    date_created = models.DateTimeField(auto_now_add=True,
                                        verbose_name=_('Date Created'))

    # temporary fix for updated profiles
    already_updated = models.BooleanField(default=False)

    GROUPS = []
    MAIL_TEMPLATE = 'accountrequest/mail_notification.jinja'

    def __str__(self):
        return "%s:%s:%s:%s" % (self.user, self.request_type, self.approved, self.date_created)

    class Meta:
        ordering = ['request_type', 'approved', 'date_created']
        unique_together = (('user', 'request_type'),)

    def get_display_value(self, property_name):
        if property_name != 'approved':
            return super(AccountRequest, self).get_display_value(property_name)
        else:
            return ('--' if self.approved is None
                    else _('Yes') if self.approved is True
                    else _('No'))

    def approve(self):
        """
        Adds the Account Request's email address to the appropriate Google
        groups, and marks the request as approved.
        """
        if self.request_type == 'volunteer':
            self.user.is_volunteer = True
            self.user.save()
        elif self.request_type == 'request':
            self.user.is_user = True
            self.user.save()

        self.approved = True
        self.save()
        self.notify_approved()

    def reject(self):
        """
        Removes the user from the group!
        """
        if self.request_type == 'volunteer':
            self.user.is_volunteer = False
            self.user.save()
        elif self.request_type == 'request':
            self.user.is_user = False
            self.user.save()

        self.approved = False
        self.save()
        self.notify_rejected()

    def notify_received(self):
        self.email_notification(
            to=self.user.email,
            subject=unicode(_('Your Account Request was received')),
            template='mail/account_request/received.jinja',
            context={'request': self}
        )
        for admin in AUTH_USER_MODEL.objects.filter(is_superuser=True):
            with templocale(admin.locale or 'en'):
                self.email_notification(
                    to=admin.email,
                    subject=unicode(_('An Account Request was received')),
                    template='mail/account_request/received_admin.jinja',
                    context={'request': self}
                )

    def notify_approved(self):
        self.email_notification(
            to=self.user.email,
            subject=unicode(_('An update to your Account Request')),
            template='mail/account_request/approved.jinja',
            context={'request': self}
        )

    def notify_rejected(self):
        self.email_notification(
            to=self.user.email,
            subject=unicode(_('Your Account Request was rejected')),
            template='mail/account_request/rejected.jinja',
            context={'request': self}
        )

    def email_notification(self, to, subject, template, context):
        pass




