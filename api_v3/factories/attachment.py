# -*- coding: utf-8 -*-

from api_v3.models import Attachment
from .profile import ProfileFactory
from .support import DjangoModelFactory, SubFactory, FileField
from .ticket import TicketFactory


class AttachmentFactory(DjangoModelFactory):

    class Meta:
        model = Attachment

    ticket = SubFactory(TicketFactory)
    user = SubFactory(ProfileFactory)
    upload = FileField(filename=u'țеșт.txt')
