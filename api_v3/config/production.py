from configurations import values
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from .common import Common


class Production(Common):

    ALLOWED_HOSTS = ['*']

    INSTALLED_APPS = (
        'gunicorn',
    ) + Common.INSTALLED_APPS

    # This router will disable the browsing of the API.
    ROUTER_CLASS = 'rest_framework.routers.SimpleRouter'

    # Sentry
    SENTRY_DSN = values.Value('', environ_name='SENTRY_DSN', environ_prefix='')

    @classmethod
    def post_setup(cls):
        sentry_sdk.init(dsn=cls.SENTRY_DSN, integrations=[DjangoIntegration()])

        super(Production, cls).post_setup()
