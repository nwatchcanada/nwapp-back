"""
Django settings for nwapp project.

Generated by 'django-admin startproject' using Django 2.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import environ
import re
from django.urls import reverse_lazy

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))



'''
django-environ
https://github.com/joke2k/django-environ
'''
root = environ.Path(__file__) - 3 # three folder back (/a/b/c/ - 3 = /)
env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)
environ.Env.read_env() # reading .env file

SITE_ROOT = root()



'''
django
https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/
'''

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY') # Raises ImproperlyConfigured exception if SECRET_KEY not in os.environ

# SECURITY WARNING: Do not run true in production environment.
DEBUG = env('DEBUG', default=False)
TEMPLATE_DEBUG = env('DEBUG', default=False)

ALLOWED_HOSTS = ['*']

SITE_ID = 1
ADMIN_ENABLED = True
ADMINS = [
    ( env("ADMIN_NAME"), env("ADMIN_EMAIL") )
]
# LOGIN_URL = reverse_lazy('nwapp_login_master')
# LOGOUT_URL = reverse_lazy('nwapp_logout_redirector')
# LOGIN_URL = 'login'
# LOGOUT_URL = 'logout'
# LOGIN_REDIRECT_URL = 'nwapp_dashboard_master' # See `dashboard/urls.py` file!

INSTALLED_APPS = [
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Extra Django Apps
    # 'django.contrib.sites',
    # 'django.contrib.sitemaps',
    'django.contrib.postgres',   # Postgres full-text search: https://docs.djangoproject.com/en/1.10/ref/contrib/postgres/search/
    'django.contrib.gis',        # Geo-Django: https://docs.djangoproject.com/en/dev/ref/contrib/gis/
    'django.contrib.humanize',   # Humanize: https://docs.djangoproject.com/en/dev/ref/contrib/humanize/

    # Third Party Apps
    'corsheaders',
    'oauth2_provider',
    'rest_framework',
    'django_filters',
    'django_rq',
    'anymail',
    'djmoney',
    # 'social_django',
    'storages',
    'redis_cache',

    # Our Apps
    'shared_foundation',
    'shared_account',
    'tenant_foundation',
    'tenant_district',
    'tenant_staff',
    'api',
    'tenant_dashboard',
]

AUTH_USER_MODEL = 'shared_foundation.SharedUser'

AUTHENTICATION_BACKENDS = [
    # # Social-sign in authentication.
    # 'social_core.backends.github.GithubOAuth2',
    # 'social_core.backends.twitter.TwitterOAuth',
    # 'social_core.backends.facebook.FacebookOAuth2',

     # Custom authentication.
    'shared_foundation.backends.NWAppEmailPasswordAuthenticationBackend',
    'shared_foundation.backends.NWAppPasswordlessAuthenticationBackend',

    # oAuth 2.0 authentication.
    'oauth2_provider.backends.OAuth2Backend',
]


MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',                  # Third Party
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.BrokenLinkEmailsMiddleware',    # Extra Django App
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'shared_foundation.middleware.schema_middleware.SchemaMiddleware', # Custom App
    'shared_foundation.middleware.ip_middleware.IPMiddleware', # Custom App
    'django.middleware.locale.LocaleMiddleware',              # Extra Django App
    'oauth2_provider.middleware.OAuth2TokenMiddleware',       # Third Party
    # 'social_django.middleware.SocialAuthExceptionMiddleware', # Third Party
]

ROOT_URLCONF = 'nwapp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR + '/templates/',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',    # Extra Django App
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # 'foundation.context_processors.constants',          # Custom App
                # 'social_django.context_processors.backends',        # Extra Django App
                # 'social_django.context_processors.login_redirect',  # Extra Django App
            ],
        },
    },
]

WSGI_APPLICATION = 'nwapp.wsgi.application'



'''
Database
https://docs.djangoproject.com/en/2.1/ref/settings/#databases
'''

DATABASES = {
    "default": {
        'CONN_MAX_AGE': 0,
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"), # YOU MUST CHANGE IN PROD!
        "HOST": env("DB_HOST"),
        "PORT": env("DB_PORT"),
    }
}



'''
Password validation
https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators
'''

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]



"""
Email
https://docs.djangoproject.com/en/1.11/topics/email/
"""

EMAIL_BACKEND = env("EMAIL_BACKEND")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")
DEFAULT_TO_EMAIL = env("DEFAULT_TO_EMAIL")



"""
Anymail
https://github.com/anymail/django-anymail
"""

ANYMAIL = {
    # (exact settings here depend on your ESP...)
    "MAILGUN_API_KEY": env("MAILGUN_ACCESS_KEY"),
    "MAILGUN_SENDER_DOMAIN": env("MAILGUN_SERVER_NAME"),
}



'''
Internationalization
https://docs.djangoproject.com/en/2.1/topics/i18n/
'''

LANGUAGE_CODE = 'en'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

ugettext = lambda s: s
LANGUAGES = (
    ('en', ugettext('English')),
#    ('fr', ugettext('French')),
#    ('es', ugettext('Spanish')),
)

LOCALE_PATHS = (
    os.path.join(BASE_DIR, "locale"),
)



'''
Static files (CSS, JavaScript, Images)
https://docs.djangoproject.com/en/2.1/howto/static-files/
'''

AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')

AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
AWS_S3_ENDPOINT_URL = env('AWS_S3_ENDPOINT_URL')
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_LOCATION = 'static'
AWS_STATIC_LOCATION = 'static'
AWS_DEFAULT_ACL = 'private'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME')
AWS_LOCATION = 'static'
STATIC_URL = '{}/{}/'.format(AWS_S3_ENDPOINT_URL, AWS_LOCATION)
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

AWS_PUBLIC_MEDIA_LOCATION = 'media/public'
DEFAULT_FILE_STORAGE = 'nwapp.s3utils.PublicMediaStorage'

AWS_PRIVATE_MEDIA_LOCATION = 'media/private'
PRIVATE_FILE_STORAGE = 'nwapp.s3utils.PrivateMediaStorage'



"""
django-redis-cache
https://github.com/sebleier/django-redis-cache
"""

CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': 'localhost:6379',
    },
}



"""
Error Reporting
https://docs.djangoproject.com/en/2.0/howto/error-reporting/
"""

IGNORABLE_404_URLS = [
    re.compile(r'^$'),
    re.compile(r'^/$'),
    re.compile(r'\.(php|cgi)$'),
    re.compile(r'^/phpmyadmin/'),
    re.compile(r'^/apple-touch-icon.*\.png$'),
    re.compile(r'^/favicon\.ico$'),
    re.compile(r'^/robots\.txt$'),
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}



'''
django-cors-headers
https://github.com/ottoyiu/django-cors-headers
'''

CORS_ORIGIN_ALLOW_ALL=True


'''
Django-REST-Framework
https://github.com/encode/django-rest-framework
'''

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
        # 'rest_framework.authentication.SessionAuthentication', # To keep the Browsable API
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        # 'rest_framework.permissions.IsAuthenticated',
        'shared_foundation.drf.permissions.DisableOptionsPermission',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    # 'DEFAULT_METADATA_CLASS': None,
    'PAGE_SIZE': 100
}



'''
django-oauth-toolkit
https://github.com/jazzband/django-oauth-toolkit
'''

OAUTH2_PROVIDER = {
    'SCOPES': {
        'read': 'Read scope',
        'write': 'Write scope',
        'introspection': 'Access to introspect resource'
    }
}
OAUTH2_PROVIDER_APPLICATION_MODEL = 'oauth2_provider.Application'
OAUTH2_PROVIDER_ACCESS_TOKEN_MODEL = 'oauth2_provider.AccessToken'



"""
django-debug-toolbar
https://django-debug-toolbar.readthedocs.io/en/stable/index.html
"""

INTERNAL_IPS = [
    '127.0.0.1',
    '0.0.0.0'
]



"""
django-rq
https://github.com/rq/django-rq
"""

RQ_QUEUES = {
    'default': {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 0,
        # 'PASSWORD': '',
        'DEFAULT_TIMEOUT': 666,
    }
}
RQ_SHOW_ADMIN_LINK = True


"""
dj-stripe
https://github.com/dj-stripe/dj-stripe
"""
STRIPE_LIVE_PUBLIC_KEY = env("STRIPE_LIVE_PUBLIC_KEY")
STRIPE_LIVE_SECRET_KEY = env("STRIPE_LIVE_SECRET_KEY")
STRIPE_TEST_PUBLIC_KEY = env("STRIPE_TEST_PUBLIC_KEY")
STRIPE_TEST_SECRET_KEY = env("STRIPE_TEST_SECRET_KEY")
STRIPE_PRODUCT = env("STRIPE_PRODUCT")
STRIPE_MONTHLY_PLAN_ID = env("STRIPE_MONTHLY_PLAN_ID")
STRIPE_MONTHLY_PLAN_AMOUNT = env("STRIPE_MONTHLY_PLAN_AMOUNT")
STRIPE_MONTHLY_PLAN_CURRENCY = env("STRIPE_MONTHLY_PLAN_CURRENCY")
STRIPE_LIVE_MODE = int(env("STRIPE_LIVE_MODE"))
DJSTRIPE_WEBHOOK_SECRET = env("DJSTRIPE_WEBHOOK_SECRET")


STRIPE_SECRET_KEY  =  env("STRIPE_TEST_SECRET_KEY")
STRIPE_PUBLIC_KEY = env("STRIPE_TEST_PUBLIC_KEY")


# """
# social-app-django
# https://github.com/python-social-auth/social-app-django
# """
# SOCIAL_AUTH_GITHUB_KEY = env("SOCIAL_AUTH_GITHUB_KEY")
# SOCIAL_AUTH_GITHUB_SECRET = env("SOCIAL_AUTH_GITHUB_SECRET")
# SOCIAL_AUTH_GITHUB_SCOPE = [
#     'read:user',
#     'user:email',
# ]
# SOCIAL_AUTH_USER_MODEL = 'foundation.User'
# SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL = True
# SOCIAL_AUTH_POSTGRES_JSONFIELD = True
# SOCIAL_AUTH_LOGIN_ERROR_URL = reverse_lazy('nwapp_profile_social_settings_detail')
# SOCIAL_AUTH_LOGIN_REDIRECT_URL = reverse_lazy('nwapp_dashboard_master')
# SOCIAL_AUTH_RAISE_EXCEPTIONS = False
# SOCIAL_AUTH_FACEBOOK_KEY = env("SOCIAL_AUTH_FACEBOOK_KEY")
# SOCIAL_AUTH_FACEBOOK_SECRET = env("SOCIAL_AUTH_FACEBOOK_SECRET")
# SOCIAL_AUTH_TWITTER_KEY = env("SOCIAL_AUTH_TWITTER_KEY")
# SOCIAL_AUTH_TWITTER_SECRET = env("SOCIAL_AUTH_TWITTER_SECRET")



'''
nwapp-back
https://github.com/nwapp/nwapp-back
'''
NWAPP_BACKEND_HTTP_PROTOCOL = env("NWAPP_BACKEND_HTTP_PROTOCOL")
NWAPP_BACKEND_HTTP_DOMAIN = env("NWAPP_BACKEND_HTTP_DOMAIN")
NWAPP_BACKEND_DEFAULT_MONEY_CURRENCY = env("NWAPP_BACKEND_DEFAULT_MONEY_CURRENCY")
NWAPP_RESOURCE_SERVER_NAME = env("NWAPP_RESOURCE_SERVER_NAME")
NWAPP_RESOURCE_SERVER_INTROSPECTION_URL = env("NWAPP_RESOURCE_SERVER_INTROSPECTION_URL")
NWAPP_RESOURCE_SERVER_INTROSPECTION_TOKEN = env("NWAPP_RESOURCE_SERVER_INTROSPECTION_TOKEN")
NWAPP_FRONTEND_HTTP_PROTOCOL = env("NWAPP_FRONTEND_HTTP_PROTOCOL")
NWAPP_FRONTEND_HTTP_DOMAIN = env("NWAPP_FRONTEND_HTTP_DOMAIN")
