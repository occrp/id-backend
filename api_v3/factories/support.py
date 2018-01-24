from factory import Faker, SubFactory #  noqa
from factory.django import DjangoModelFactory, FileField # noqa


# Use a locale with unicodes
Faker._DEFAULT_LOCALE = 'es_ES'
