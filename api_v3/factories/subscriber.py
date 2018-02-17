from api_v3.models import Subscriber
from .profile import ProfileFactory
from .support import DjangoModelFactory, SubFactory
from .ticket import TicketFactory


class SubscriberFactory(DjangoModelFactory):

    class Meta:
        model = Subscriber

    ticket = SubFactory(TicketFactory)
    user = SubFactory(ProfileFactory)
