# -*- coding: utf-8 -*-
import os

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret! Change for your local setup!
SECRET_KEY = '2342##_1DFAKJkja;lkjs_117854*((*(!_sdfajkkj728k'
CREDENTIALS_DIR = 'data/credentials/'

ALLOWED_HOSTS = ["127.0.0.1:8000"]


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
DATABASE_ENGINE = 'django.db.backends.postgresql_psycopg2'
DATABASE_HOST = '127.0.0.1'
DATABASE_PORT = '5432'
DATABASE_NAME = 'test'
DATABASE_USER = os.environ.get('PG_USER')
DATABASE_PASSWORD = os.environ.get('PG_PASSWORD')

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/
TIME_ZONE = 'UTC'
LANGUAGE_CODE = 'en-us'
DATE_FORMAT = 'd-F-Y'

PODACI_ES_SERVERS = ["localhost:9333"]
PODACI_ES_INDEX = 'podaci_test'
PODACI_FS_ROOT = 'data_test'

#application defaults
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

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),
    'PAGE_SIZE': 10
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
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
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'log.log',
            'maxBytes': 1024*1024*5,  # 5 MB
            'backupCount': 5,
            'formatter': 'verbose'
        },
    },
    'loggers': {
        '': {  # root logger defined by empty string
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propogate': True
        },
        'elasticsearch': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propogate': True
        }
    }
}
