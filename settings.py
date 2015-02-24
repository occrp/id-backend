"""
Django settings for id project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(__file__)
print "Working directory: %s" % (BASE_DIR)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '^!#g4j-0$=%2pzv@f+^!+4ovq@e_gctly)924jgskq(sd!y(6*'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1:8020"]

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

ROOT_URLCONF = 'urls'

# FIXME: Move existing templates to .jinja, start writing
#        new templates as .html with Django template engine
DEFAULT_JINJA2_TEMPLATE_EXTENSION = '.html'

JINJA_EXTS = (
    'jinja2.ext.i18n',
)


# WSGI_APPLICATION = 'id.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)
STATIC_URL = '/static/'


## Investigative Dashboard Default Settings!
from django.utils.translation import ugettext_lazy as _

DEFAULTS = {
    'search' : {
        'result_limit': 100,
        'index_version': '1',
    },

    'ticket_notifications': {
        'update': ['requester', 'responders', 'admin'],
        'charge': ['requester', 'responders', 'admin'],
        'paid': ['requester', 'responders', 'admin'],
        'close': ['requester', 'responders', 'admin'],
        'cancel': ['requester', 'responders', 'admin'],
        'reopen': ['requester', 'responders', 'admin'],
        'open': ['requester', 'responders', 'admin'],
        'flag': ['requester', 'responders', 'admin'],
        'docs_changed': ['requester', 'responder', 'admin'],
        'entities_attached': ['requester', 'responder', 'admin']
    },
}

PODACI_SERVERS = [{"host": "localhost"}]
PODACI_ES_INDEX = "podaci"
PODACI_FS_ROOT = "/home/id/data/"

