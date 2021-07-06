from api_v3.models import Review
from .support import DjangoModelFactory, Faker, SubFactory
from .ticket import TicketFactory


class ReviewFactory(DjangoModelFactory):

    class Meta:
        model = Review

    ticket = SubFactory(TicketFactory)
    body = Faker('bs')
