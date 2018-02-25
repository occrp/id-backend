from .common import Common


class Production(Common):

    ALLOWED_HOSTS = ['*']

    INSTALLED_APPS = (
        'gunicorn',
        'raven.contrib.django.raven_compat',
    ) + Common.INSTALLED_APPS

    # This router will disable the browsing of the API.
    ROUTER_CLASS = 'rest_framework.routers.SimpleRouter'
