import logging

from factory import Faker, SubFactory  # noqa
from factory.django import DjangoModelFactory, FileField  # noqa
from factory.faker import faker # noqa


# Silence noisy third-party loggers...
logging.getLogger('faker').setLevel(logging.ERROR)
logging.getLogger('factory').setLevel(logging.ERROR)

# Use a locale with unicodes
Faker._DEFAULT_LOCALE = 'es_ES'
