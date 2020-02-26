from datetime import datetime

from django.db import models
from django.conf import settings
from djmoney.models.fields import MoneyField
from moneyed.classes import CURRENCIES

from .ticket import Ticket


class Expense(models.Model):
    """Ticket expense model."""

    ticket = models.ForeignKey(
        Ticket, blank=False, related_name='expenses', db_index=True,
        on_delete=models.DO_NOTHING)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=False, db_index=True,
        on_delete=models.DO_NOTHING)

    amount = MoneyField(
        max_digits=19, decimal_places=4, null=True,
        default_currency=CURRENCIES['USD'].code)

    notes = models.TextField(blank=False, null=False)
    created_at = models.DateTimeField(default=datetime.utcnow)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def filter_by_user(cls, user, queryset=None):
        """Returns any user accessible expenses.

        Only ticket responders have access to the expenses.
        """
        return (queryset or cls.objects).filter(
            ticket__responder_users=user
        )
