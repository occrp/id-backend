from djmoney.settings import CURRENCY_CHOICES

from api_v3.models import Expense
from .profile import ProfileFactory
from .support import DjangoModelFactory, Faker, SubFactory
from .ticket import TicketFactory


class ExpenseFactory(DjangoModelFactory):

    class Meta:
        model = Expense

    ticket = SubFactory(TicketFactory)
    user = SubFactory(ProfileFactory)
    notes = Faker('bs')
    amount = Faker('random_number', digits=3)
    amount_currency = Faker(
        'random_element', elements=[s[0] for s in CURRENCY_CHOICES])
