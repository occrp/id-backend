from datetime import datetime, timedelta

from django.conf import settings
from django.db import models
from django_bleach.models import BleachField

import jwt

from .ticket import Ticket


class Review(models.Model):
    """Ticket review model."""

    MAX_DAYS_TO_RESPOND = 7

    # Was our response helpful?
    RATINGS = (
        (0, 'Not at all'),
        (1, 'Partly'),
        (2, 'Yes'),
        (3, 'Exceeded expectations')
    )

    ticket = models.ForeignKey(
        Ticket, blank=False, related_name='reviews', db_index=True,
        on_delete=models.DO_NOTHING)

    rating = models.IntegerField(
        default=RATINGS[1][0], choices=RATINGS, db_index=True)
    link = models.CharField(max_length=255, blank=False, null=True)
    body = BleachField(blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def ticket_to_token(cls, ticket):
        """Generates an expiring JWT token with the ticket ID."""
        return jwt.encode(
            {
                'sub': ticket.id,
                'exp': (
                    datetime.utcnow() +
                    timedelta(days=cls.MAX_DAYS_TO_RESPOND)
                )
            },
            settings.SECRET_KEY,
            algorithm='HS256'
        )

    @classmethod
    def ticket_from_token(cls, token):
        """Extracts the ticket ID from a valid JWT token."""
        if token is None or token == '':
            return None

        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=['HS256'])

            return Ticket.objects.get(id=payload.get('sub'))
        except jwt.ExpiredSignatureError:
            return None
