from django.conf import settings
from django.db import models


class Responder(models.Model):
    """Model for ticket responders."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, db_index=True,
        on_delete=models.DO_NOTHING)
    ticket = models.ForeignKey(
        'Ticket', related_name='responders', db_index=True,
        on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'ticket')

    @classmethod
    def filter_by_user(cls, user, queryset=None):
        """Returns any user responder objects.

        Either related to the tickets he created or he is subscribed to.
        """
        if queryset is None:
            queryset = cls.objects

        return queryset.filter(
            # Allow own responder objects
            models.Q(user=user) |
            # Allow related to user responder tickets
            models.Q(ticket__responder_users=user) |
            # Allow related to user subscribed tickets
            models.Q(ticket__subscriber_users=user) |
            # Allow related to user created tickets
            models.Q(ticket__requester=user)
        )
