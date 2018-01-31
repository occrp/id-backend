from django.conf import settings
from django.db import models


class Subscriber(models.Model):
    """Ticket subscriber."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, db_index=True)
    ticket = models.ForeignKey(
        'Ticket', related_name='subscribers', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'ticket')

    @classmethod
    def filter_by_user(cls, user, queryset=None):
        """Returns any user subscriber objects.

        Either related to the tickets he created or he is subscribed to.
        """
        return (queryset or cls.objects).filter(
            # Allow own subscriber objects
            models.Q(user=user) |
            # Allow related to user subscriber tickets
            models.Q(ticket__users=user) |
            # Allow related to user created tickets
            models.Q(ticket__requester=user)
        )
