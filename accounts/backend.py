import requests
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
        groups = response.get('groups')
        return {
            'username': response.get('username'),
            'email': response.get('email'),
            'first_name': response.get('firstName'),
            'last_name': response.get('lastName'),
            'is_staff': 'functionStaff' in groups,
            'is_superuser': 'functionSuperuser' in groups,
        }

    def user_data(self, access_token, *args, **kwargs):
        res = requests.post(self.USERINFO_URL, headers={
            'Authorization': 'Bearer %s' % access_token
        })
        # print res.json()
        return res.json()
