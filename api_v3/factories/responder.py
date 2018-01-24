from api_v3.models import Responder
from .profile import ProfileFactory
from .support import DjangoModelFactory, SubFactory
from .ticket import TicketFactory


class ResponderFactory(DjangoModelFactory):

    class Meta:
        model = Responder

    ticket = SubFactory(TicketFactory)
    user = SubFactory(ProfileFactory)
