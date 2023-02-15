from django.conf import settings
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django_bleach.models import BleachField

from .countries import COUNTRIES
from .responder import Responder
from .subscriber import Subscriber


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

    PRIORITIES = (
        ('low', 'Low'),
        ('default', 'Default'),
        ('high', 'High'),
    )

    KINDS = (
        ('person_ownership', 'Identify what a person owns'),
        ('company_ownership', 'Determine company ownership'),
        ('vehicle_tracking', 'Vehicle tracking'),
        ('data_request', 'Data request'),
        ('other', 'Any other question')
    )

    MIN_SEARCH_RANK = 0.3

    SEARCH_WEIGHT_MAP = {
        'first_name': 'A',
        'last_name': 'A',
        'company_name': 'A',
        'comments__body': 'A',
        'comments__user__email': 'A',
        'comments__user__first_name': 'A',
        'comments__user__last_name': 'A',
        'background': 'B',
        'connections': 'C',
        'sources': 'C',
        'business_activities': 'C',
        'initial_information': 'C',
        'whysensitive': 'C',
    }

    responder_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through=Responder,
        related_name='responder_tickets')
    subscriber_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through=Subscriber,
        related_name='subscriber_tickets')
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='requested_tickets',
        db_index=True, on_delete=models.DO_NOTHING)

    kind = models.CharField(
        blank=False, max_length=70, choices=KINDS,
        default=KINDS[-1][0], db_index=True)
    request_type = models.CharField(
        blank=False, max_length=70, choices=TYPES,
        default=TYPES[0][0], db_index=True)
    status = models.CharField(
        max_length=70, choices=STATUSES,
        default=STATUSES[0][0], db_index=True)
    priority = models.CharField(
        max_length=70, choices=PRIORITIES,
        default=PRIORITIES[1][0], db_index=True)

    sensitive = models.BooleanField(default=False)
    whysensitive = BleachField(max_length=150, null=True, blank=True)
    deadline_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_notifications_at = models.DateTimeField(null=True)
    member_center = BleachField(max_length=512, null=True, blank=False)
    identifier = BleachField(max_length=512, null=True, blank=True)
    countries = ArrayField(
        models.CharField(max_length=255, null=True, blank=False),
        default=list,
        db_index=True)
    tags = ArrayField(
        models.CharField(max_length=255, null=True, blank=False),
        default=list,
        db_index=True)

    # Other ticket type fields, also common to all other types
    background = BleachField(blank=False)

    # Person ticket type fields
    first_name = BleachField(max_length=512, null=True, blank=True)
    last_name = BleachField(max_length=512, null=True, blank=True)
    born_at = models.DateTimeField(null=True)
    connections = BleachField(null=True, blank=True)
    sources = BleachField(null=True, blank=True)
    business_activities = BleachField(null=True, blank=True)
    initial_information = BleachField(null=True, blank=True)

    # Company ticket type fields
    company_name = BleachField(max_length=512, null=True, blank=True)
    country = models.CharField(
        max_length=100, choices=COUNTRIES, null=True, db_index=True, blank=True)

    @property
    def users(self):
        return (
            self.responder_users.all() |
            self.subscriber_users.all()
        ).distinct()

    @classmethod
    def filter_by_user(cls, user, queryset=None):
        """Returns any user tickets.

        Either the ones he created or he is subscribed to.
        """
        if queryset is None:
            queryset = cls.objects

        return queryset.filter(
            # Allow ticket authors
            models.Q(requester=user) |
            # Allow ticket responders
            models.Q(responder_users=user) |
            # Allow ticket subscribers
            models.Q(subscriber_users=user)
        ).distinct()

    @classmethod
    def search_for(cls, keywords, queryset=None):
        """Full text ticket search.

        Returns an annotated query set.
        """
        query = SearchQuery(keywords)
        vector = None

        if queryset is None:
            queryset = cls.objects

        for field, weight in list(cls.SEARCH_WEIGHT_MAP.items()):
            if not vector:
                vector = SearchVector(field, weight=weight)
            else:
                vector += SearchVector(field, weight=weight)

        return queryset.annotate(
            rank=SearchRank(vector, query)
        ).filter(
            rank__gte=cls.MIN_SEARCH_RANK
        ).distinct().order_by('rank')
