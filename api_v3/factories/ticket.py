from api_v3.models import Ticket
from .profile import ProfileFactory
from .support import DjangoModelFactory, SubFactory, Faker


class TicketFactory(DjangoModelFactory):

    class Meta:
        model = Ticket

    requester = SubFactory(ProfileFactory)

    status = Faker(
        'random_element', elements=map(lambda s: s[0], Ticket.STATUSES))
    kind = Faker(
        'random_element', elements=map(lambda k: k[0], Ticket.KINDS))
    request_type = Faker(
        'random_element', elements=map(lambda t: t[0], Ticket.TYPES))
    sensitive = Faker('random_element', elements=[True, False])
    whysensitive = Faker('catch_phrase')
    deadline_at = Faker('future_datetime', end_date='+30d')

    background = Faker('bs')

    first_name = Faker('first_name')
    last_name = Faker('last_name')
    born_at = Faker('past_datetime', start_date='-30y')
    connections = Faker('company')
    sources = Faker('name')
    business_activities = Faker('catch_phrase')

    company_name = Faker('company')
    country = Faker('country')
