# -*- coding: utf-8 -*-

from factory import Faker, SubFactory
from factory.django import DjangoModelFactory, FileField

from .models import Profile, Ticket, Responder, Attachment, Comment


# Use a locale with unicodes
Faker._DEFAULT_LOCALE = 'es_ES'


class ProfileFactory(DjangoModelFactory):

    class Meta:
        model = Profile

    email = Faker('email')
    first_name = Faker('first_name')
    last_name = Faker('last_name')
    bio = Faker('job')
    last_login = Faker('past_date', start_date='-30d')


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
    deadline_at = Faker('future_date', end_date='+30d')

    background = Faker('bs')

    first_name = Faker('first_name')
    last_name = Faker('last_name')
    born_at = Faker('past_date', start_date='-30y')
    connections = Faker('company')
    sources = Faker('name')
    business_activities = Faker('catch_phrase')

    company_name = Faker('company')
    country = Faker('country')


class ResponderFactory(DjangoModelFactory):

    class Meta:
        model = Responder

    ticket = SubFactory(TicketFactory)
    user = SubFactory(ProfileFactory)


class AttachmentFactory(DjangoModelFactory):

    class Meta:
        model = Attachment

    ticket = SubFactory(TicketFactory)
    user = SubFactory(ProfileFactory)
    upload = FileField(filename=u'țеșт.txt')


class CommentFactory(DjangoModelFactory):

    class Meta:
        model = Comment

    ticket = SubFactory(TicketFactory)
    user = SubFactory(ProfileFactory)
    body = Faker('bs')
