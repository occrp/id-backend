from django.db import models
from django.conf import settings
from activity.models import Action  # noqa

from core.countries import COUNTRIES
from accounts.models import Profile  # noqa
from ticket.constants import REQUESTER_TYPES, TICKET_STATUS, TICKET_TYPES


class Responder(models.Model):
    """Intermediate model for ticket responders (M2M)."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, db_index=True)
    ticket = models.ForeignKey(
        'Ticket', related_name='responders', db_index=True)

    class Meta:
        unique_together = ('user', 'ticket')


class Ticket(models.Model):
    """Ticket model."""

    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through=Responder, db_index=True)
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='requested_tickets',
        db_index=True)

    kind = models.CharField(
        blank=False, max_length=70, choices=TICKET_TYPES,
        default=TICKET_TYPES[-1][0], db_index=True)
    request_type = models.CharField(
        blank=False, max_length=70, choices=REQUESTER_TYPES,
        default=REQUESTER_TYPES[0][0], db_index=True)
    status = models.CharField(
        max_length=70, choices=TICKET_STATUS,
        default=TICKET_STATUS[0][0], db_index=True)

    sensitive = models.BooleanField(default=False)
    whysensitive = models.CharField(max_length=150, blank=True)
    deadline_at = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Other ticket type fields, also common to all other types
    background = models.TextField(blank=False, max_length=1000)

    # Person ticket type fields
    first_name = models.CharField(max_length=512, blank=True)
    last_name = models.CharField(max_length=512, blank=True)
    born_at = models.DateField(null=True, blank=True)
    connections = models.TextField(blank=True)
    sources = models.TextField(blank=True)
    business_activities = models.TextField(blank=True, max_length=1000)
    initial_information = models.TextField(max_length=1000, blank=True)

    # Company ticket type fields
    company_name = models.CharField(max_length=512, blank=True)
    country = models.CharField(
        max_length=100, choices=COUNTRIES, blank=True, db_index=True)

    @classmethod
    def filter_by_user(cls, user, queryset=None):
        """Returns any user tickets.

        Either the ones he created or he is subscribed to.
        """
        return (queryset or cls.objects).filter(
            # Allow ticket authors to send attachments
            models.Q(requester=user) |
            # Allow ticket responders to send attachments
            models.Q(users=user)
        )


class Attachment(models.Model):
    """Ticket attachment model."""

    ticket = models.ForeignKey(
        Ticket, blank=False, related_name='attachments', db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=False, db_index=True)
    upload = models.FileField(
        upload_to='{}/attachments/%Y/%m/%d'.format(settings.DOCUMENT_PATH))
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def filter_by_user(cls, user, queryset=None):
        """Returns any user accessible attachments.

        Either the ones he created or he has access to through the tickets.
        """
        return (queryset or cls.objects).filter(
            # Let ticket authors see ticket attachments
            models.Q(ticket__requester=user) |
            # Let ticket responders see tickets attachments
            models.Q(ticket__users=user) |
            # Let attachment authors see own attachments
            models.Q(user=user)
        )


class Comment(models.Model):
    """Ticket comment model."""

    ticket = models.ForeignKey(
        Ticket, blank=False, related_name='comments', db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=False, db_index=True)

    body = models.TextField(blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def filter_by_user(cls, user, queryset=None):
        """Returns any user accessible comments.

        Either the ones he created or he has access to through the tickets.
        """
        return (queryset or cls.objects).filter(
            # Let ticket authors see ticket attachments
            models.Q(ticket__requester=user) |
            # Let ticket responders see tickets attachments
            models.Q(ticket__users=user) |
            # Let attachment authors see own attachments
            models.Q(user=user)
        )
