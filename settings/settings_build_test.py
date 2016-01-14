# -*- coding: utf-8 -*-
import os
# import the defaults so that we have something to work with
from settings_defaults import *

# SECURITY WARNING: keep the secret key used in production secret! Change for your local setup!
SECRET_KEY = '2342##_1DFAKJkja;lkjs_117854*((*(!_sdfajkkj728k'
CREDENTIALS_DIR = 'data/credentials/'
ALLOWED_HOSTS = ["127.0.0.1:8000"]


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
DATABASE_HOST = '127.0.0.1'
DATABASE_PORT = '5432'
DATABASE_NAME = 'test'
DATABASE_USER = os.environ.get('PG_USER')
DATABASE_PASSWORD = os.environ.get('PG_PASSWORD')
PODACI_ES_SERVERS = ["localhost:9233"]
PODACI_ES_INDEX = 'podaci_test'
PODACI_FS_ROOT = 'data_test'


LOGGING['handlers']['file'['filename'] = 'log.log'

LOGGING['loggers']['elasticsearch'] = {
    'handlers': ['file'],
    'level': 'DEBUG',
    'propogate': True
}
