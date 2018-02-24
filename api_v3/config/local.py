import uuid

from .common import Common


class Local(Common):

    DEBUG = True

    SECRET_KEY = uuid.uuid4().hex

    # Testing
    INSTALLED_APPS = Common.INSTALLED_APPS

    # Mail
    EMAIL_HOST = 'localhost'
    EMAIL_PORT = 1025
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

    INSTALLED_APPS = Common.INSTALLED_APPS + (
        'django.contrib.staticfiles',
        'django_extensions',
    )
