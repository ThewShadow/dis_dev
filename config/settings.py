"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 4.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""
import os
from pathlib import Path
from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
debug = os.environ.get('DEBUG', 0)
if int(debug) == 1:
    DEBUG = True
else:
    DEBUG = False
print(f'debug {DEBUG}')

BASE_URL = os.environ.get('BASE_URL', '')
NGROK_DOMAIN = os.environ.get('NGROK_DOMAIN', '')

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '5.189.164.30']

CSRF_TRUSTED_ORIGINS = [
    'http://localhost',
    'https://www.paypalobjects.com',
    'http://127.0.0.1',
    'https://5.189.164.30'
]

if NGROK_DOMAIN:
    ALLOWED_HOSTS.append(NGROK_DOMAIN.replace('https://', ''))
    CSRF_TRUSTED_ORIGINS.append(NGROK_DOMAIN)

if BASE_URL:
    ALLOWED_HOSTS.append(BASE_URL.replace('https://', ''))
    CSRF_TRUSTED_ORIGINS.append(BASE_URL)

SECURE_CROSS_ORIGIN_OPENER_POLICY='same-origin-allow-popups'

# Application definition

INSTALLED_APPS = [
    'modeltranslation',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'main.apps.MainConfig',
    'phonenumber_field',
    'service.apps.ServiceConfig',
    'debug_toolbar',

]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'main.middleware.ExceptionLoggingMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',

]

INTERNAL_IPS = [
    "127.0.0.1",
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            'main/templates',
            'service/templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'main.context_processors.base_context',
            ],

        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        # 'ENGINE': 'django.db.backends.postgresql_psycopg2',
        # 'NAME': os.environ.get('SQL_DATABASE'),
        # 'USER': os.environ.get('SQL_USER'),
        # 'PASSWORD': os.environ.get('SQL_PASSWORD'),
        # 'HOST': os.environ.get('SQL_HOST'),
        # 'PORT': os.environ.get('SQL_PORT')
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

LANGUAGES = (
    ('en', _('English')),
    ('ru', _('Russian')),
    ('es', _('Spanish')),
    ('fr', _('France')),
    ('he', _('Hebrew')),
)

MODELTRANSLATION_DEFAULT_LANGUAGE = 'en'
MODELTRANSLATION_PREPOPULATE_LANGUAGE = 'en'

USE_MODELTRANSLATION = True

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
MEDIA_ROOT = os.path.join(BASE_DIR, "media")


# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/service/accounts/login/'
LOGIN_REDIRECT_URL = '/profile/info/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_ERROR_URL = '/unauthorized/'
ACCOUNT_ACTIVATION_DAYS = 3
AUTH_USER_EMAIL_UNIQUE = True

AUTH_USER_MODEL = 'main.CustomUser'


AUTHENTICATION_BACKENDS = (
    'main.backends.EmailBackend',
)

EMAIL_BACKEND = 'django_smtp_ssl.SSLEmailBackend'

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET')

EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = 465
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = False
DEFAULT_FROM_EMAIL = 'example@gmail.comv'
MANAGERS_EMAILS = ['zvichayniy.vick@gmail.com', 'futuredevback1@gmail.com']

VERIFY_CODE_LENGTH = 6

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] [{module}] [{levelname}]: {message}',
            'style': '{',
            'datefmt': '%Y/%m/%d %H:%M:%S'
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': 'debug.log'
        },
    },
    'loggers': {
        'main': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': False,

        }
    },
}

TELEGRAM_BOT_API_KEY = os.environ.get('TELEGRAM_BOT_API_KEY')
TELEGRAM_GROUP_MANAGERS_ID = os.environ.get('TELEGRAM_GROUP_MANAGERS_ID')

PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID')

