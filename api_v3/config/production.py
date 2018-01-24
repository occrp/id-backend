from .common import Common


class Production(Common):

    ALLOWED_HOSTS = ['*']

    INSTALLED_APPS = (
        'gunicorn',
        'raven.contrib.django.raven_compat',
    ) + Common.INSTALLED_APPS
