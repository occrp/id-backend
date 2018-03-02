import uuid

from .common import Common


class Local(Common):

    DEBUG = True

    SECRET_KEY = uuid.uuid4().hex

    # Testing
    INSTALLED_APPS = Common.INSTALLED_APPS

    INSTALLED_APPS = Common.INSTALLED_APPS + (
        'django.contrib.staticfiles',
        'django_extensions',
    )

    SOCIAL_AUTH_KEYCLOAK_BASE = Common.SOCIAL_AUTH_KEYCLOAK_BASE
    SOCIAL_AUTH_KEYCLOAK_BASE.environ_required = False
    SOCIAL_AUTH_KEYCLOAK_KEY = Common.SOCIAL_AUTH_KEYCLOAK_KEY
    SOCIAL_AUTH_KEYCLOAK_KEY.environ_required = False
    SOCIAL_AUTH_KEYCLOAK_SECRET = Common.SOCIAL_AUTH_KEYCLOAK_SECRET
    SOCIAL_AUTH_KEYCLOAK_SECRET.environ_required = False

    DEFAULT_FROM_EMAIL = Common.DEFAULT_FROM_EMAIL
    DEFAULT_FROM_EMAIL.environ_required = False
