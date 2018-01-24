from django.conf import settings
from django.db import models


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
