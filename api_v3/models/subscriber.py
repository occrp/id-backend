from django.conf import settings
from django.db import models


class Subscriber(models.Model):
    """Ticket subscriber."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, db_index=True, null=True)
    ticket = models.ForeignKey(
        'Ticket', related_name='subscribers', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    email = models.CharField(max_length=512, blank=True, null=True)

    class Meta:
        unique_together = (
            ('user', 'email', 'ticket')
        )

    @classmethod
    def filter_by_user(cls, user, queryset=None):
        """Returns any user subscriber objects.

        A subscriber is very much similar to a responder, but:
            * it can not do ticket updates
            * it can not add other people to a ticket.

        Either related to the tickets he created or he is subscribed to.
        """
        return (queryset or cls.objects).filter(
            # Allow own subscriber objects
            models.Q(user=user) |
            # Allow related to user responder tickets
            models.Q(ticket__responder_users=user) |
            # Allow related to user subscribed tickets
            models.Q(ticket__subscriber_users=user) |
            # Allow related to user created tickets
            models.Q(ticket__requester=user)
        )
