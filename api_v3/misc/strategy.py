from django.contrib.sessions.backends.base import SessionBase
from social_django.strategy import DjangoStrategy


class Strategy(DjangoStrategy):
    """Patched strategy to provide a fake session when middleware is not used"""

    def __init__(self, storage, request=None, tpl=None):

        if not hasattr(request, 'session'):
            setattr(request, 'session', SessionBase())

        super(Strategy, self).__init__(storage, request, tpl)
