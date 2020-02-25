from api_v3.models import Ticket
from api_v3.models.countries import COUNTRIES
from .profile import ProfileFactory
from .support import DjangoModelFactory, SubFactory, Faker


class TicketFactory(DjangoModelFactory):

    class Meta:
        model = Ticket

    requester = SubFactory(ProfileFactory)

    status = Faker(
        'random_element', elements=[s[0] for s in Ticket.STATUSES])
    kind = Faker(
        'random_element', elements=[k[0] for k in Ticket.KINDS])
    request_type = Faker(
        'random_element', elements=[t[0] for t in Ticket.TYPES])
    priority = Faker(
        'random_element', elements=[t[0] for t in Ticket.PRIORITIES])
    sensitive = Faker('random_element', elements=[True, False])
    whysensitive = Faker('catch_phrase')
    deadline_at = Faker('future_datetime', end_date='+30d')
    countries = Faker(
        'random_sample', elements=[t[0] for t in COUNTRIES], length=3)

    background = Faker('bs')

    first_name = Faker('first_name')
    last_name = Faker('last_name')
    born_at = Faker('past_datetime', start_date='-30y')
    connections = Faker('company')
    sources = Faker('name')
    business_activities = Faker('catch_phrase')

    company_name = Faker('company')
    country = Faker('random_element', elements=[c[0] for c in COUNTRIES])
