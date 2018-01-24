from django.conf import settings
from django.db import models

from .countries import COUNTRIES
from .responder import Responder


class Ticket(models.Model):
    """Ticket model."""

    TYPES = (
        # Subsidized: we pay for everything)
        ('subs', 'Subsidized'),
        # Covering cost: we pay for labor, person pays costs of buying documents
        ('cost', 'Covering Cost'),
        # Covering cost+: person pays for everything
        ('cost_plus', 'Covering Cost +')
    )

    STATUSES = (
        ('new', 'New'),
        ('in-progress', 'In Progress'),
        ('pending', 'Pending'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled')
    )

    KINDS = (
        ('person_ownership', 'Identify what a person owns'),
        ('company_ownership', 'Determine company ownership'),
        ('other', 'Any other question')
    )

    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through=Responder, db_index=True)
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='requested_tickets',
        db_index=True)

    kind = models.CharField(
        blank=False, max_length=70, choices=KINDS,
        default=KINDS[-1][0], db_index=True)
    request_type = models.CharField(
        blank=False, max_length=70, choices=TYPES,
        default=TYPES[0][0], db_index=True)
    status = models.CharField(
        max_length=70, choices=STATUSES,
        default=STATUSES[0][0], db_index=True)

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
