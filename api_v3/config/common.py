import os.path
import tempfile

from configurations import Configuration, values


class Common(Configuration):

    VERSION = values.Value('0.0.0-x', environ_prefix='ID')
    SITE_NAME = values.Value('Investigative Dashboard', environ_prefix='ID')

    INSTALLED_APPS = (
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.auth',

        # Third party apps
        'rest_framework',
        'corsheaders',
        'django_filters',
        'social_django',
        'activity',

        # Your apps
        'api_v3',

    )

    MIDDLEWARE = (
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'corsheaders.middleware.CorsMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
    )

    ALLOWED_HOSTS = ["*"]
    ROOT_URLCONF = 'api_v3.urls'
    SECRET_KEY = values.SecretValue()
    WSGI_APPLICATION = 'api_v3.wsgi.application'
    USE_X_FORWARDED_HOST = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    ROUTER_CLASS = 'rest_framework.routers.DefaultRouter'

    # Email
    EMAIL = values.EmailURLValue('console://')
    DEFAULT_FROM_EMAIL = values.EmailValue(
        '', environ_prefix='ID', environ_required=True)
    DEFAULT_FROM = '{} <{}>'.format(SITE_NAME, DEFAULT_FROM_EMAIL)

    ADMINS = []

    # Postgres
    DATABASES = values.DatabaseURLValue(
        'postgres://postgres:@postgres:5432/postgres')

    # CORS
    CORS_ALLOW_CREDENTIALS = True
    CORS_ORIGIN_WHITELIST = values.ListValue(['localhost:8000'])
    CORS_ORIGIN_ALLOW_ALL = values.BooleanValue(False)

    # Sentry
    RAVEN_CONFIG = {
        'dsn': values.Value('', environ_name='SENTRY_DSN'),
        'release': VERSION,
    }

    # General
    APPEND_SLASH = False
    TIME_ZONE = 'UTC'
    LANGUAGE_CODE = 'en-us'
    # If you set this to False, Django will make some optimizations so as not
    # to load the internationalization machinery.
    USE_I18N = False
    USE_L10N = False
    USE_TZ = False

    # Media files: max. size of 500MB
    MEDIA_ROOT = values.Value(tempfile.gettempdir(), environ_name='MEDIA_ROOT')
    MAX_UPLOAD_SIZE = 1024 * 1024 * 500
    STATIC_URL = '/api/static/'

    DEBUG = values.BooleanValue(False)

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'APP_DIRS': True,
            'DIRS': [
                os.path.abspath(
                    os.path.join(os.path.dirname(__file__), '..', 'templates')
                ),
            ],
        },
    ]

    # Logging
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {
            'require_debug_true': {
                '()': 'django.utils.log.RequireDebugTrue',
            },
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            '': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': True,
            },
        }
    }

    # Custom user app
    AUTH_USER_MODEL = 'api_v3.Profile'

    # Authentication
    AUTHENTICATION_BACKENDS = values.ListValue(
        [
            'api_v3.misc.oauth2.KeycloakOAuth2',
            'django.contrib.auth.backends.ModelBackend',
        ]
    )
    SOCIAL_AUTH_KEYCLOAK_BASE = values.Value(
        '', environ_prefix='', environ_required=True)
    SOCIAL_AUTH_KEYCLOAK_KEY = values.Value(
        '', environ_prefix='', environ_required=True)
    SOCIAL_AUTH_KEYCLOAK_SECRET = values.Value(
        '', environ_prefix='', environ_required=True)

    # Username is not used.
    SOCIAL_AUTH_USER_FIELDS = ['email']

    # See: http://python-social-auth.readthedocs.io/en/latest/pipeline.html
    SOCIAL_AUTH_PIPELINE = (
        'social_core.pipeline.social_auth.social_details',
        'social_core.pipeline.social_auth.social_uid',
        'social_core.pipeline.social_auth.social_user',
        'social_core.pipeline.social_auth.associate_by_email',
        'social_core.pipeline.user.create_user',
        'social_core.pipeline.social_auth.associate_user',
        'social_core.pipeline.user.user_details',
        'api_v3.misc.oauth2.activate_user',
    )

    # Django Rest Framework
    REST_FRAMEWORK = {
        'DEFAULT_PERMISSION_CLASSES': [
            'rest_framework.permissions.IsAuthenticated',
        ],
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'rest_framework.authentication.SessionAuthentication',
        )
    }

    # JSON API DRF
    JSON_API_FORMAT_KEYS = 'dasherize'
    JSON_API_FORMAT_TYPES = 'dasherize'
    JSON_API_PLURALIZE_TYPES = True
