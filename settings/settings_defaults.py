# -*- coding: utf-8 -*-

##################
#
#   Sane default settings
#   potentially overridden by settings from
#   settings_local.py, settings_production.py, or settings_build_test.py
#
##################

# by default these are false, for SECURITY! and great justice!
# change manually if you need that
DEBUG = True
TEMPLATE_DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret! Change for your local setup!
SECRET_KEY = 'lk;jsaoipas0202lknasdlsadfasdfdsakhao2f2sdfasfdsafdsafdsafasdfdsafdsafaib23jsk'
CREDENTIALS_DIR = 'data/credentials'

# this should be done better, but for the time being it will have to do
# because nginx container does not have a static IP
ALLOWED_HOSTS = ["*",]
EMERGENCY = None

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
DATABASE_NAME = 'id2'
DATABASE_USER = 'id2'
DATABASE_PASSWORD = 'HiedaighohThoo7Dal3aiYei'
# configuration for PostgreSQL
DATABASE_ENGINE = 'django.db.backends.postgresql_psycopg2'
DATABASE_HOST = 'postgres'
DATABASE_PORT = '5432'

# our own precious User model
# as per: https://docs.djangoproject.com/en/dev/topics/auth/customizing/
AUTH_USER_MODEL = 'id.Profile'

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/
TIME_ZONE = 'UTC'
LANGUAGE_CODE = 'en-us'
DATE_FORMAT = 'd-F-Y'

PODACI_FS_ROOT = '/data'

# Application defaults
DEFAULTS = {
    'search': {
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
        'audit': {
            'level': 'INFO',
            'class': 'core.log.AuditLogHandler',
        }
    },
    'loggers': {
        '': {  # root logger defined by empty string
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
}

# HTTPS if needed
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTOCOL", "https")

ADMINS = (('OCCRP Tech', 'tech@occrp.org'),)
MANAGERS = (('OCCRP Tech', 'tech@occrp.org'),)

EMAIL_HOST_USER = "id@occrp.org"
EMAIL_HOST_PASSWORD = ""  # this has to be set in settings_production.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = 'Investigative Dashboard <id@occrp.org>'
