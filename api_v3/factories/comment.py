from api_v3.models import Comment
from .profile import ProfileFactory
from .support import DjangoModelFactory, Faker, SubFactory
from .ticket import TicketFactory


class CommentFactory(DjangoModelFactory):

    class Meta:
        model = Comment

    ticket = SubFactory(TicketFactory)
    user = SubFactory(ProfileFactory)
    body = Faker('bs')
