# -*- coding: utf-8 -*-
"""
Django settings for Investigative Dashboard
"""
import os
here = lambda x: os.path.realpath(os.path.join(os.path.realpath(os.path.dirname(__file__)), x))
BASE_DIR = here('../')

ID_VERSION = "2.2.0"
ID_ENVIRONMENT = os.environ.get('ID_ENVIRONMENT', 'debug')
print "Starting ID version %s (%s)" % (ID_VERSION, ID_ENVIRONMENT)

ALLOWED_HOSTS = []
EMERGENCY = False

##################
#
#   Template loaders and such
#
##################

from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS
TEMPLATE_CONTEXT_PROCESSORS += (
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.csrf",
    "settings.context_processors.locale",
    "settings.context_processors.routename",
    'social.apps.django_app.context_processors.backends',
    'social.apps.django_app.context_processors.login_redirect'
)

TEMPLATE_LOADERS = (
    'django_jinja.loaders.FileSystemLoader',
    'django_jinja.loaders.AppLoader',
)

TEMPLATE_DIRS = ('templates',)


##################
#
#   Import local settings or production settings
#
##################

#
# default settings reside in settings_defaults.py (duh!).
#
# depending on the value of ID_ENVIRONMENT, we try loading different files:
# "debug"      - settings_local.py
# "production" - settings_production.py
# "testing"    - settings_build_test.py
#
# if the file exists, it is assumed to contain all the settings that we expect from
# settings_defaults.py, potentially with some changes here and there
#
# the sane way of doing this is importing all the settings from settings_defaults.py
# in such a file, and modifying just the parts that are meeded to be modified
#
# example in settings_production.py-example
#
# if a given file is not found, settings from settings_defaults.py are loaded directly
#

try:
    if ID_ENVIRONMENT == 'testing' or os.environ.get('BUILD_TEST'):
        from settings_build_test import *
    elif ID_ENVIRONMENT == 'production':
        from settings_production import *
    elif ID_ENVIRONMENT == 'debug':
        from settings_local import *

except ImportError:
    # which file are we talking about?
    if ID_ENVIRONMENT == 'testing' or os.environ.get('BUILD_TEST'):
        fname = "settings_build_test.py"
    elif ID_ENVIRONMENT == 'production':
        fname = "settings_production.py"
    elif ID_ENVIRONMENT == 'debug':
        fname = "settings_local.py"

    # inform
    print "WARNING: failed importing settings from %s (probably the file does not exist), using settings_defaults.py" % fname
    from settings_defaults import * # if that fails, we're boned


##################
#
#   Debug-related settings
#
##################
if DEBUG:
        # credentials for {testing,staging}.occrp.org
        GOOGLE_OAUTH2_CLIENT_ID      = '206887598454-df3pp9ldb8367vu544hkmjvlpsl9gg46.apps.googleusercontent.com'
        GOOGLE_OAUTH2_CLIENT_SECRET  = 'y2hZUFTrCj-IgIrPf3jpTE2d'

        from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS
        TEMPLATE_CONTEXT_PROCESSORS += (
            "django.core.context_processors.request",
            "django.contrib.messages.context_processors.messages",
            "django.core.context_processors.csrf",
            "settings.context_processors.locale",
            "settings.context_processors.routename",
            "settings.context_processors.debug",
        )


##################
#
#   Some error checking for local_settings
#
##################

if not SECRET_KEY:
    raise Exception('You need to specify Django SECRET_KEY in the settings_local.py!')

if "CREDENTIALS_DIR" not in vars():
    raise Exception('You need to specify a path to CREDENTIALS_DIR in settings_local.py')


##################
#
#   Apps
#
##################

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
    'social.apps.django_app.default',
    'accounts',
    'core',
    'databases',
    'feedback',
    'podaci',
    'ticket',
    'django_select2',
    'captcha',
    'oauth2_provider',
)

##################
#
#   Authentication
#
##################

SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.social_user',
    'social.pipeline.user.get_username',
    'social.pipeline.social_auth.associate_by_email',
    'social.pipeline.user.create_user',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details',
    'core.auth.activate_user'
)

# google settings, potentially overridden in settings_local
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '206887598454-nigepmham8557t4uq72dqhgh159p3b1t.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'f6b3cUIp00sDoiRSLfyqAQkH'
SOCIAL_AUTH_USER_MODEL = 'accounts.Profile'
SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL = True
USER_FIELDS = ['email']

AUTHENTICATION_BACKENDS = (
    'rules.permissions.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
    'social.backends.google.GoogleOAuth2',
)

if DEBUG:
    SOCIAL_AUTH_RAISE_EXCEPTIONS = True
    RAISE_EXCEPTIONS = True

# our own precious User model
# as per: https://docs.djangoproject.com/en/dev/topics/auth/customizing/
AUTH_USER_MODEL = 'accounts.Profile'
# SOCIAL_AUTH_SESSION_EXPIRATION = False # TODO: This shouldn't be done

# registration form class
# from id.forms import ProfileRegistrationForm
# REGISTRATION_FORM=ProfileRegistrationForm
# is the registration alowed?
REGISTRATION_OPEN = True
# set to an URL that a user should be redirected to when registration is off
REGISTRATION_CLOSED_URL = "/accounts/register/closed/"
# set to an URL that a user should be redirected upon successful registration
REGISTRATION_SUCCESS_URL = "/accounts/register/complete/"


##################
#
#   Middleware
#
##################

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social.apps.django_app.middleware.SocialAuthExceptionMiddleware'
)

ROOT_URLCONF = 'settings.urls'
AUTO_RENDER_SELECT2_STATICS = False
DEFAULT_JINJA2_TEMPLATE_EXTENSION = '.jinja'

from django_jinja.builtins import DEFAULT_EXTENSIONS

JINJA2_EXTENSIONS = DEFAULT_EXTENSIONS + [
    "jinja2.ext.i18n",
    "compressor.contrib.jinja2ext.CompressorExtension",
]

##################
#
#   Static files (CSS, JavaScript, Images, compression)
#   https://docs.djangoproject.com/en/1.6/howto/static-files/
#
##################

STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)
# STATIC_ROOT = os.path.join(BASE_DIR, "static_gen")
STATIC_URL = '/static/'

COMPRESS_ROOT = os.path.join(BASE_DIR, "static")

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

COMPRESS_ENABLED = False


##################
#
#   Database defaults
#   https://docs.djangoproject.com/en/1.6/ref/settings/#databases
#
##################

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


##################
#
#   Internationalization
#   https://docs.djangoproject.com/en/1.6/topics/i18n/
#
##################

USE_I18N = True
USE_L10N = True
USE_TZ = False

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

from django.conf.global_settings import DATE_INPUT_FORMATS
DATE_INPUT_FORMATS += ('%d/%m/%y',)

##################
#
#   REST Framework
#
##################

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'oauth2_provider.ext.rest_framework.OAuth2Authentication',
    ),
    'PAGE_SIZE': 30
}
