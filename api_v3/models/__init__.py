from activity.models import Action
from django.db.models.signals import post_save
from django.dispatch import receiver

from .attachment import Attachment  # noqa
from .comment import Comment  # noqa
from .expense import Expense  # noqa
from .profile import Profile  # noqa
from .responder import Responder  # noqa
from .review import Review  # noqa
from .subscriber import Subscriber  # noqa
from .ticket import Ticket  # noqa


@receiver(post_save, sender=Action)
def touch_ticket_updated(instance, **kwargs):
    if isinstance(instance.target, Ticket):
        instance.target.updated_at = instance.timestamp
        instance.target.save(update_fields=['updated_at'])
