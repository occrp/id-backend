import jwt
from urlparse import urljoin
from social.backends.oauth import BaseOAuth2
from django.conf import settings


class KeycloakOAuth2(BaseOAuth2):
    """Keycloak OAuth authentication backend"""
    name = 'keycloak'

    path = '/auth/realms/%s/' % settings.KEYCLOAK_REALM
    ID_KEY = 'email'
    KEYCLOAK_BASE = urljoin(settings.KEYCLOAK_URL, path)
    USERINFO_URL = urljoin(KEYCLOAK_BASE, 'protocol/openid-connect/userinfo')
    AUTHORIZATION_URL = urljoin(KEYCLOAK_BASE, 'protocol/openid-connect/auth')
    ACCESS_TOKEN_URL = urljoin(KEYCLOAK_BASE, 'protocol/openid-connect/token')
    ACCESS_TOKEN_METHOD = 'POST'

    def get_user_details(self, response):
        clients = response.get('resource_access', {})
        client = clients.get(settings.SOCIAL_AUTH_KEYCLOAK_KEY, {})
        roles = set(client.get('roles', []))

        return {
            'username': response.get('preferred_username'),
            'email': response.get('email'),
            'first_name': response.get('given_name'),
            'last_name': response.get('family_name'),
            'is_staff': 'staff' in roles,
            'is_superuser': 'superuser' in roles,
        }

    def user_data(self, access_token, *args, **kwargs):
        return jwt.decode(access_token, verify=False)
