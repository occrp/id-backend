from django.conf import settings
from social_core.backends.oauth import BaseOAuth2
import jwt


class KeycloakOAuth2(BaseOAuth2):
    """Keycloak OAuth authentication backend"""

    name = 'keycloak'

    ID_KEY = 'email'
    USERINFO_URL = settings.KEYCLOAK_BASE + 'protocol/openid-connect/userinfo'
    AUTHORIZATION_URL = settings.KEYCLOAK_BASE + 'protocol/openid-connect/auth'
    ACCESS_TOKEN_URL = settings.KEYCLOAK_BASE, 'protocol/openid-connect/token'
    ACCESS_TOKEN_METHOD = 'POST'

    def get_user_details(self, response):
        clients = response.get('resource_access', {})
        client = clients.get(settings.KEYCLOAK_KEY, {})
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

    @classmethod
    def activate_user(cls, backend, user, response, *args, **kwargs):
        user.is_active = True
        user.save()
