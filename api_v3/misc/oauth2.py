import collections.abc
from urllib.parse import urljoin

from django.conf import settings
import jwt
from social_core.backends.oauth import BaseOAuth2

from ..models import Subscriber, Action

# Patch `social-core` for Python 3.9 compatibility:
#   See: https://github.com/python-social-auth/social-core/pull/424/files
setattr(collections, 'Callable', collections.abc.Callable)


class KeycloakOAuth2(BaseOAuth2):
    """Keycloak OAuth authentication backend"""

    name = 'keycloak'

    ID_KEY = 'email'
    BASE_URL = settings.SOCIAL_AUTH_KEYCLOAK_BASE
    USERINFO_URL = urljoin(BASE_URL, 'protocol/openid-connect/userinfo')
    AUTHORIZATION_URL = urljoin(BASE_URL, 'protocol/openid-connect/auth')
    ACCESS_TOKEN_URL = urljoin(BASE_URL, 'protocol/openid-connect/token')
    ACCESS_TOKEN_METHOD = 'POST'

    def get_user_details(self, response):
        clients = response.get('resource_access', {})
        client = clients.get(settings.SOCIAL_AUTH_KEYCLOAK_KEY, {})
        roles = set(client.get('roles', []))

        return {
            'email': response.get('email'),
            'first_name': response.get('given_name'),
            'last_name': response.get('family_name'),
            'is_staff': 'staff' in roles,
            'is_superuser': 'superuser' in roles,
        }

    def user_data(self, access_token, *args, **kwargs):
        return jwt.decode(
            access_token,
            algorithms=['RS256', 'HS256'],
            options={'verify_signature': False}
        )


def activate_user(backend, user, *args, **kwargs):
    """This will activate an user account, unless it is not active."""
    if not user.is_active:
        user.is_active = True
        user.save()


def map_email_to_subscriber(backend, user, *args, **kwargs):
    """This will map new users email to existing subscriber records."""
    for subscriber in Subscriber.objects.filter(email=user.email):
        subscriber.user = user
        subscriber.email = None
        subscriber.save()

        Action.objects.create(
            actor=user, target=subscriber.ticket,
            action=subscriber.user, verb='subscriber:update:joined'
        )
