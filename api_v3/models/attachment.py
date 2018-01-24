from django.conf import settings
from django.db import models

from .ticket import Ticket


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
