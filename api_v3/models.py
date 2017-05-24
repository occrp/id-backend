from django.db import models
from django.conf import settings

from core.models import Notification  # noqa
from core.mixins import NotificationMixin
from core.countries import COUNTRIES
from accounts.models import Profile  # noqa
from ticket.constants import REQUESTER_TYPES, TICKET_STATUS, TICKET_TYPES


class Ticket(models.Model, NotificationMixin):
    """Ticket model."""

    responders = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='assigned_tickets',
        db_index=True)
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='requested_tickets',
        db_index=True)

    kind = models.CharField(
        blank=False, max_length=70, choices=TICKET_TYPES, db_index=True)
    request_type = models.CharField(
        blank=False, max_length=70, choices=REQUESTER_TYPES, db_index=True)
    status = models.CharField(
        max_length=70, choices=TICKET_STATUS, default='new', db_index=True)

    sensitive = models.BooleanField(default=False)
    whysensitive = models.CharField(max_length=150, blank=True)
    deadline_at = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Other ticket type fields, also common to all other types
    background = models.TextField(blank=False, max_length=1000)

    # Person ticket type fields
    first_name = models.CharField(max_length=512, blank=False)
    last_name = models.CharField(max_length=512, blank=False)
    born_at = models.DateField(null=True, blank=True)
    connections = models.TextField(blank=True)
    sources = models.TextField(blank=True)
    activities = models.TextField(blank=False, max_length=1000)
    initial_information = models.TextField(max_length=1000, blank=False)

    # Company ticket type fields
    company_name = models.CharField(max_length=512, blank=False)
    country = models.CharField(
        max_length=100, choices=COUNTRIES, blank=False, db_index=True)


class Attachment(models.Model, NotificationMixin):
    """Record for a file attached to a ticket."""

    ticket = models.ForeignKey(
        Ticket, blank=False, related_name='attachments', db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=False, db_index=True)
    upload = models.FileField(upload_to='attachments/%Y/%m/%d')
    created_at = models.DateTimeField(auto_now_add=True)
