from api_v3.models import Profile
from .support import DjangoModelFactory, Faker


class ProfileFactory(DjangoModelFactory):

    class Meta:
        model = Profile

    email = Faker('email')
    first_name = Faker('first_name')
    last_name = Faker('last_name')
    bio = Faker('job')
    last_login = Faker('past_date', start_date='-30d')
