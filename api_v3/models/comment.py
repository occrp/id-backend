from django.db import models
from django.conf import settings

from .ticket import Ticket


class Comment(models.Model):
    """Ticket comment model."""

    ticket = models.ForeignKey(
        Ticket, blank=False, related_name='comments', db_index=True,
        on_delete=models.DO_NOTHING)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=False, db_index=True,
        on_delete=models.DO_NOTHING)

    body = models.TextField(blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def filter_by_user(cls, user, queryset=None):
        """Returns any user accessible comments.

        Ones he has access to through the tickets.
        """
        return (queryset or cls.objects).filter(
            ticket__in=Ticket.filter_by_user(user)
        )
