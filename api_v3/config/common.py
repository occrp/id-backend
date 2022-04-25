import os.path

from configurations import Configuration, values


class Common(Configuration):

    VERSION = values.Value('0.0.0-x', environ_prefix='ID')
    SITE_NAME = values.Value('OCCRP ID', environ_prefix='ID')

    INSTALLED_APPS = (
        'django.contrib.contenttypes',
        'django.contrib.auth',
        'django.contrib.sessions',

        # Third party apps
        'rest_framework',
        'corsheaders',
        'django_filters',
        'social_django',
        'activity',
        'djmoney',
        'django_bleach',

        # Your apps
        'api_v3',

    )

    MIDDLEWARE = (
        'django.middleware.security.SecurityMiddleware',
        'corsheaders.middleware.CorsMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
    )

    ALLOWED_HOSTS = ["*"]
    ROOT_URLCONF = 'api_v3.urls'
    SECRET_KEY = values.SecretValue()
    WSGI_APPLICATION = 'api_v3.wsgi.application'
    USE_X_FORWARDED_HOST = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    ROUTER_CLASS = 'rest_framework.routers.DefaultRouter'

    # Email, defaults to in-memory backend, switch to `console` for development
    EMAIL = values.EmailURLValue('locmem://')
    DEFAULT_FROM_EMAIL = values.EmailValue(
        '', environ_prefix='ID', environ_required=True)
    DEFAULT_FROM = '{} <{}>'.format(SITE_NAME, DEFAULT_FROM_EMAIL)
    DEFAULT_NOTIFY_EMAILS = values.ListValue([], environ_prefix='ID')

    ADMINS = []

    # Postgres
    DATABASES = values.DatabaseURLValue(
        'postgres://postgres:postgres@postgres:5432/postgres')
    QUEUE_DATABASE_URL = values.Value(
        'postgres://postgres:postgres@postgres:5432/postgres',
        environ_name='QUEUE_DATABASE_URL', environ_prefix='')

    # CORS
    CORS_ALLOW_CREDENTIALS = True
    CORS_ORIGIN_WHITELIST = values.ListValue(['http://localhost:8000'])
    CORS_ORIGIN_ALLOW_ALL = values.BooleanValue(False)

    # Misc
    EXPENSE_SCOPES = values.ListValue([], environ_prefix='ID')
    MEMBER_CENTERS = values.ListValue([], environ_prefix='ID')

    # General
    APPEND_SLASH = False
    TIME_ZONE = 'UTC'
    LANGUAGE_CODE = 'en-us'
    # If you set this to False, Django will make some optimizations so as not
    # to load the internationalization machinery.
    USE_I18N = False
    USE_L10N = False
    USE_TZ = False

    # Sanitization
    BLEACH_ALLOWED_TAGS = []
    BLEACH_ALLOWED_ATTRIBUTES = []
    BLEACH_STRIP_TAGS = True
    BLEACH_STRIP_COMMENTS = True

    # Media files: max. size of 500MB
    MEDIA_ROOT = values.Value(
        environ_name='MEDIA_ROOT', environ_prefix='', environ_required=True)
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
        ]
    )
    SOCIAL_AUTH_KEYCLOAK_BASE = values.Value('', environ_prefix='')
    SOCIAL_AUTH_KEYCLOAK_KEY = values.Value('', environ_prefix='')
    SOCIAL_AUTH_KEYCLOAK_SECRET = values.Value('', environ_prefix='')
    SOCIAL_AUTH_NO_DEFAULT_PROTECTED_USER_FIELDS = values.BooleanValue(
        True, environ_prefix='')
    SOCIAL_AUTH_PROTECTED_USER_FIELDS = values.ListValue([], environ_prefix='')

    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = values.Value('', environ_prefix='')
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = values.Value('', environ_prefix='')

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
        'api_v3.misc.oauth2.map_email_to_subscriber',
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
    JSON_API_FORMAT_FIELD_NAMES = 'dasherize'
    JSON_API_FORMAT_TYPES = 'dasherize'
    JSON_API_PLURALIZE_TYPES = True

    # Default job queue name
    QUEUE_NAME = values.Value('default', environ_prefix='')

    # Allows disabling the review emails
    REVIEWS_DISABLED = values.BooleanValue(False, environ_prefix='ID')
