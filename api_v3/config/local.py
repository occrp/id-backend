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

    KEYCLOAK_BASE = Common.KEYCLOAK_BASE
    KEYCLOAK_BASE.environ_required = False
    KEYCLOAK_KEY = Common.KEYCLOAK_KEY
    KEYCLOAK_KEY.environ_required = False
    KEYCLOAK_SECRET = Common.KEYCLOAK_SECRET
    KEYCLOAK_SECRET.environ_required = False

    EMAIL_RECIPIENT = Common.EMAIL_RECIPIENT
    EMAIL_RECIPIENT.environ_required = False
    DEFAULT_FROM_EMAIL = Common.DEFAULT_FROM_EMAIL
    DEFAULT_FROM_EMAIL.environ_required = False
