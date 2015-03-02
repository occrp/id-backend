"""
Django settings for id project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""
import os
here = lambda x: os.path.realpath(os.path.join(os.path.realpath(os.path.dirname(__file__)), x))
BASE_DIR = here('../')


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/


ALLOWED_HOSTS = []

try:
    if os.environ.get('BUILD_TEST'):
        from settings_build_test import *
    else:
        from settings_local import *

except ImportError:
    raise Exception('You need to set up settings_local.py (see settings_local.py-example')

# Some error checking for local_settings
if not SECRET_KEY:
    raise Exception('You need to specify Django SECRET_KEY in the settings_local.py!')

TEMPLATE_LOADERS = (
    'django_jinja.loaders.FileSystemLoader',
    'django_jinja.loaders.AppLoader',
)

TEMPLATE_DIRS = ('templates',)

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'registration',
    'django_jinja',
    'id',
    'podaci',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS
TEMPLATE_CONTEXT_PROCESSORS += (
    "django.core.context_processors.request",
    "id.context_processors.locale",
    "id.context_processors.routename",
    "id.context_processors.userprofile",
)

ROOT_URLCONF = 'settings.urls'

# FIXME: Move existing templates to .jinja, start writing
#        new templates as .html with Django template engine
DEFAULT_JINJA2_TEMPLATE_EXTENSION = '.html'

JINJA_EXTS = (
    'jinja2.ext.i18n',
    'podaci.templatetags.mentions'
)


# WSGI_APPLICATION = 'id.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': DATABASE_ENGINE,
        'NAME': DATABASE_NAME,
        'USER': DATABASE_USER,
        'PASSWORD': DATABASE_PASSWORD,
        'HOST': DATABASE_HOST,
        'PORT': DATABASE_PORT,
    }
}


NEO4J_DATABASES = {
    'default': {
        'HOST': NEO4J_HOST,
        'PORT': NEO4J_PORT,
        'ENDPOINT': NEO4J_ENDPOINT
    }
}

# DATABASE_ROUTERS = ['neo4django.utils.Neo4djangoIntegrationRouter']


# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)
STATIC_URL = '/static/'


# Investigative Dashboard Default Settings!
from django.utils.translation import ugettext_lazy as _


PODACI_SERVERS = [{"host": "localhost"}]
PODACI_ES_INDEX = 'podaci'
PODACI_FS_ROOT = '/home/id/data/'
