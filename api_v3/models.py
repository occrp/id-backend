from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from activity.models import Action  # noqa

from core.countries import COUNTRIES
from accounts.models import Profile  # noqa
from ticket.constants import REQUESTER_TYPES, TICKET_STATUS, TICKET_TYPES


class Responder(models.Model):
    """Intermediate model for ticket responders (M2M)."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, db_index=True)
    ticket = models.ForeignKey(
        'Ticket', related_name='responders', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'ticket')

    @classmethod
    def filter_by_user(cls, user, queryset=None):
        """Returns any user responder objects.

        Either related to the tickets he created or he is subscribed to.
        """
        return (queryset or cls.objects).filter(
            # Allow own responder objects
            models.Q(user=user) |
            # Allow related to user responder tickets
            models.Q(ticket__users=user) |
            # Allow related to user created tickets
            models.Q(ticket__requester=user)
        )


class Ticket(models.Model):
    """Ticket model."""

    STATUSES = TICKET_STATUS
    KINDS = TICKET_TYPES
    TYPES = REQUESTER_TYPES

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
    whysensitive = models.CharField(max_length=150, null=True, blank=True)
    deadline_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_notifications_at = models.DateTimeField(null=True)

    # Other ticket type fields, also common to all other types
    background = models.TextField(blank=False)

    # Person ticket type fields
    first_name = models.CharField(max_length=512, null=True, blank=True)
    last_name = models.CharField(max_length=512, null=True, blank=True)
    born_at = models.DateTimeField(null=True)
    connections = models.TextField(max_length=1000, null=True, blank=True)
    sources = models.TextField(max_length=1000, null=True, blank=True)
    business_activities = models.TextField(
        null=True, max_length=1000, blank=True)
    initial_information = models.TextField(
        max_length=1000, null=True, blank=True)

    # Company ticket type fields
    company_name = models.CharField(max_length=512, null=True, blank=True)
    country = models.CharField(
        max_length=100, choices=COUNTRIES, null=True, db_index=True, blank=True)

    @classmethod
    def filter_by_user(cls, user, queryset=None):
        """Returns any user tickets.

        Either the ones he created or he is subscribed to.
        """
        return (queryset or cls.objects).filter(
            # Allow ticket authors
            models.Q(requester=user) |
            # Allow ticket responders
            models.Q(users=user)
        ).distinct()


class Attachment(models.Model):
    """Ticket attachment model."""

    ticket = models.ForeignKey(
        Ticket, blank=False, related_name='attachments', db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=False, db_index=True)
    upload = models.FileField(upload_to='attachments/%Y/%m/%d', max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def filter_by_user(cls, user, queryset=None):
        """Returns any user accessible attachments.

        Either the ones he created or he has access to through the tickets.
        """
        return (queryset or cls.objects).filter(
            # Let ticket authors and responders see ticket attachments
            models.Q(ticket__in=Ticket.filter_by_user(user)) |
            # Let attachment authors see own attachments
            models.Q(user=user) |
            # Let ticket users see superuser attachments
            models.Q(user__is_superuser=True)
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
            # Let ticket authors and responders see ticket attachments
            models.Q(ticket__in=Ticket.filter_by_user(user)) |
            # Let attachment authors
            models.Q(user=user) |
            # Let ticket users see superuser comments
            models.Q(user__is_superuser=True)
        )


@receiver(post_save, sender=Action)
def touch_ticket_updated(instance, **kwargs):
    if isinstance(instance.target, Ticket):
        instance.target.updated_at = instance.timestamp
        instance.target.save()
