from django.conf import settings
from django.db import models

from .ticket import Ticket


class Attachment(models.Model):
    """Ticket attachment model."""

    ticket = models.ForeignKey(
        Ticket, blank=False, related_name='attachments', db_index=True,
        on_delete=models.DO_NOTHING)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=False, db_index=True,
        on_delete=models.DO_NOTHING)
    upload = models.FileField(upload_to='attachments/%Y/%m/%d', max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def filter_by_user(cls, user, queryset=None):
        """Returns any user accessible attachments.

        Ones he has access to through the tickets.
        """
        if queryset is None:
            queryset = cls.objects

        return queryset.filter(ticket__in=Ticket.filter_by_user(user))
