from urlparse import urljoin

from django.conf import settings
import jwt
from social_core.backends.oauth import BaseOAuth2


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
        return jwt.decode(access_token, verify=False)


def activate_user(backend, user, response, *args, **kwargs):
    user.is_active = True
    user.save()
