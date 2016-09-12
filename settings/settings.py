# -*- coding: utf-8 -*-
"""Settings for Investigative Dashboard."""

# cf. https://12factor.net/config
import os
import dj_database_url
from django.conf.global_settings import DATE_INPUT_FORMATS

BASE_DIR = os.path.join(os.path.realpath(os.path.dirname(__file__)), '../')

ID_VERSION = "2.4.0"
ID_ENVIRONMENT = os.environ.get('ID_ENVIRONMENT', 'debug')
DEBUG = ID_ENVIRONMENT == 'debug'
ID_SITE_NAME = 'Investigative Dashboard'

print "Starting %s, v. %s (%s)" % (ID_SITE_NAME, ID_VERSION, ID_ENVIRONMENT)

ALLOWED_HOSTS = ["*", ]
EMERGENCY = os.environ.get('ID_EMERGENCY', False)


##################
#
#   Template loaders and such
#
##################

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'environment': 'core.jinja2.environment'
        }
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                # "django.core.context_processors.request",
                # "django.contrib.messages.context_processors.messages",
                # "django.core.context_processors.csrf",
                # 'social.apps.django_app.context_processors.backends',
                # 'social.apps.django_app.context_processors.login_redirect'
            ]
        },
    },
]


##################
#
#   Security-related settings.
#
##################

SECRET_KEY = os.environ.get("ID_SECRET_KEY")
assert SECRET_KEY, 'You need to specify ID_SECRET_KEY in the env!'

# HTTPS if needed
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTOCOL", "https")


##################
#
#   Apps
#
##################

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.admin.apps.SimpleAdminConfig',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'registration',
    'rest_framework',
    'social.apps.django_app.default',
    'accounts',
    'core',
    'databases',
    'ticket',
    'rules.apps.AutodiscoverRulesConfig',
    'django_select2',
    'captcha',
    'oauth2_provider',
)

##################
#
#   Authentication
#
##################

AUTHENTICATION_BACKENDS = (
    'rules.permissions.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
    'social.backends.google.GoogleOAuth2',
)

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

# our own precious User model
# as per: https://docs.djangoproject.com/en/dev/topics/auth/customizing/
AUTH_USER_MODEL = 'accounts.Profile'

# google settings, potentially overridden in settings_local
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get('ID_GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get('ID_GOOGLE_OAUTH2_SECRET')
SOCIAL_AUTH_USER_MODEL = AUTH_USER_MODEL
SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL = True
USER_FIELDS = ['email']

# registration form class
# is the registration alowed?
REGISTRATION_OPEN = True
# set to an URL that a user should be redirected to when registration is off
REGISTRATION_CLOSED_URL = "/accounts/register/closed/"
# set to an URL that a user should be redirected upon successful registration
REGISTRATION_SUCCESS_URL = "/accounts/register/complete/"


OAUTH2_PROVIDER = {
    'SCOPES': {
        'read': 'Read scope',
        'write': 'Write scope',
    },
    'DEFAULT_SCOPES': ['read']
}

##################
#
#   Middleware
#
##################

MIDDLEWARE = (
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'social.apps.django_app.middleware.SocialAuthExceptionMiddleware'
)

ROOT_URLCONF = 'settings.urls'
AUTO_RENDER_SELECT2_STATICS = False

##################
#
#   Static files (CSS, JavaScript, Images, compression)
#   https://docs.djangoproject.com/en/1.6/howto/static-files/
#
##################

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)
STATIC_URL = '/static/'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

##################
#
#   Storage and database
#
##################

ID_DATABASE_URL = os.environ.get('ID_DATABASE_URL')
DATABASES = {
    'default': dj_database_url.config(default=ID_DATABASE_URL)
}

# Location for uploaded ticket attachments.
DOCUMENT_PATH = os.environ.get('ID_DOCUMENT_PATH', '/data')

# 500mb upload limit:
MAX_UPLOAD_SIZE = 1024 * 1024 * 500


##################
#
#   Application defaults
#
##################

DEFAULTS = {
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


##################
#
#   Internationalization
#   https://docs.djangoproject.com/en/1.6/topics/i18n/
#
##################

TIME_ZONE = 'UTC'
LANGUAGE_CODE = 'en-us'
DATE_FORMAT = 'd-F-Y'

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

DATE_INPUT_FORMATS += ('%d/%m/%y',)


##################
#
#   E-Mail
#
##################

EMAIL_HOST_USER = os.environ.get('ID_EMAIL_USER', 'id@occrp.org')
EMAIL_HOST_PASSWORD = os.environ.get('ID_EMAIL_PASSWORD')
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('ID_EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('ID_EMAIL_PORT', 587))
EMAIL_USE_TLS = EMAIL_PORT == 587
DEFAULT_FROM = '%s <id@occprp.org>' % ID_SITE_NAME
DEFAULT_FROM_EMAIL = os.environ.get('ID_EMAIL_FROM', DEFAULT_FROM)

ID_EMAIL_RECIPIENT_NAME = '%s Admin' % ID_SITE_NAME
ID_EMAIL_RECIPIENT = os.environ.get('ID_EMAIL_RECIPIENT', 'tech@occrp.org')

ADMINS = ((ID_EMAIL_RECIPIENT_NAME, ID_EMAIL_RECIPIENT),)
MANAGERS = ((ID_EMAIL_RECIPIENT_NAME, ID_EMAIL_RECIPIENT),)


##################
#
#   Logging
#
##################

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'mail_admins': {
            'class': 'django.utils.log.AdminEmailHandler',
            'level': 'WARNING',
            # But the emails are plain text by default - HTML is nicer
            'include_html': True,
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/id2/log.log',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'verbose'
        },
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['null'],
            'level': 'DEBUG',
            'propagate': False,
        },
        '': {  # root logger defined by empty string
            'handlers': ['console', 'file', 'mail_admins'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
}


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


##################
#
#   Debug-related settings
#
##################

if DEBUG:

    # Disable log file and emails to admins for debug mode:
    LOGGING['handlers'].pop('file')
    LOGGING['handlers'].pop('mail_admins')
    LOGGING['loggers']['']['handlers'] = ['console']

    SOCIAL_AUTH_RAISE_EXCEPTIONS = True
    RAISE_EXCEPTIONS = True
