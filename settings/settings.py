# -*- coding: utf-8 -*-
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

try: ID_VERSION = open(".git_current_version").read()
except: ID_VERSION = "?.?.? Unknown: ID Version could not be read: .git_current_version not available"
print "Starting ID version %s" % ID_VERSION

# Allowed hosts:
ALLOWED_HOSTS = []

# https://api.opencorporates.com/documentation/API-Reference#api_accounts
OPENCORPORATES_API_TOKEN = None

# Import local settings or production settings
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

if "CREDENTIALS_DIR" not in vars():
    raise Exception('You need to specify a path to CREDENTIALS_DIR in settings_local.py')

TEMPLATE_LOADERS = (
    'django_jinja.loaders.FileSystemLoader',
    'django_jinja.loaders.AppLoader',
)


TEMPLATE_DIRS = ('templates',)

# Application definition

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'registration',
    'compressor',
    'django_jinja',
    'rest_framework',
    'social_auth',

    'core',
    'id',
    'search',
    'podaci',
    # 'osoba',
    'robots',
    'ticket',
    'projects',
    'django_select2'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'podaci.middleware.PodaciExceptionMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'social_auth.backends.google.GoogleOAuth2Backend',
    'rules.permissions.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
)
GOOGLE_OAUTH2_CLIENT_ID      = '206887598454-nigepmham8557t4uq72dqhgh159p3b1t.apps.googleusercontent.com'
GOOGLE_OAUTH2_CLIENT_SECRET  = 'f6b3cUIp00sDoiRSLfyqAQkH'

# our own precious User model
# as per: https://docs.djangoproject.com/en/dev/topics/auth/customizing/
AUTH_USER_MODEL = 'id.Profile'
SOCIAL_AUTH_USER_MODEL = 'id.Profile'

# registration form class
#from id.forms import ProfileRegistrationForm
#REGISTRATION_FORM=ProfileRegistrationForm
# is the registration alowed?
REGISTRATION_OPEN=True
# set to an URL that a user should be redirected to when registration is disallowed
REGISTRATION_CLOSED_URL="/accounts/register/closed/"
# set to an URL that a user should be redirected upon successful registration
REGISTRATION_SUCCESS_URL="/accounts/register/complete/"

from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS
TEMPLATE_CONTEXT_PROCESSORS += (
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.csrf",
    "id.context_processors.locale",
    "id.context_processors.routename",
    "search.context_processors.search_types",
)

ROOT_URLCONF = 'settings.urls'

AUTO_RENDER_SELECT2_STATICS = False

# FIXME: Move existing templates to .jinja, start writing
#        new templates as .jinja with Django template engine
DEFAULT_JINJA2_TEMPLATE_EXTENSION = '.jinja'

from django_jinja.builtins import DEFAULT_EXTENSIONS

JINJA2_EXTENSIONS = DEFAULT_EXTENSIONS + [
    "jinja2.ext.i18n",
    "compressor.contrib.jinja2ext.CompressorExtension",
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)
# STATIC_ROOT = os.path.join(BASE_DIR, "static_gen")
STATIC_URL = '/static/'

COMPRESS_ROOT = os.path.join(BASE_DIR, "static")

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

# COMPRESS_ENABLED = True

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


# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = (
    ('ar', u'العربية'),
    ('bg', u'Български'),
    ('de', u'Deutsch'),
    ('en', u'English'),
    ('es', u'Español'),
    ('fr', u'Français'),
    ('hr', u'Hrvatski'),
    ('hu', u'Magyar'),
    ('mk', u'Македонски'),
    ('pt', u'Português'),
    ('ro', u'Românește'),
    ('ru', u'Русский'),
    ('sl', u'Slovenski'),
    ('sq', u'Shqip'),
    ('sr', u'Српски'),
    ('sw', u'Kiswahili'),
    ('tr', u'Türkçe'),
    ('uk', u'Українська'),
)

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES':
        ('rest_framework.permissions.IsAuthenticated',),
    'PAGE_SIZE': 30
}

from django.conf.global_settings import DATE_INPUT_FORMATS
DATE_INPUT_FORMATS += ('%d/%m/%y',)

# Investigative Dashboard Default Settings!
from django.utils.translation import ugettext_lazy as _
