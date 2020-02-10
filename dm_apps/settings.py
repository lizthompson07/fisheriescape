"""
Django settings for dm_apps project.

Generated by 'django-admin startproject' using Django 2.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
from django.utils.translation import gettext_lazy as _
from decouple import config, UndefinedValueError

# Custom variables
WEB_APP_NAME = "DMApps"

# check to see if there is a user-defined local configuration file
# if there is, we we use this as our local configuration, otherwise we use the default
try:
    from . import my_conf as local_conf
except ModuleNotFoundError and ImportError:
    from . import default_conf as local_conf

    print("my_conf.py' not found. using default configuration file 'default_conf.py' instead.")
else:
    print("using custom configuration file: 'my_conf.py'.")

PRODUCTION_SERVER = local_conf.PRODUCTION_SERVER
USING_PRODUCTION_DB = local_conf.USING_PRODUCTION_DB
USING_LOCAL_DB = local_conf.USING_LOCAL_DB
try:
    DEBUG_ON = local_conf.DEBUG
except AttributeError:
    DEBUG_ON = False

DEV_DB_NAME = local_conf.DEV_DB_NAME
DEV_DB_HOST = local_conf.DEV_DB_HOST

# check to see if there is a file containing the google api key
# if there is not, set this to a null string and maps will open in dev mode
try:
    GOOGLE_API_KEY = config("GOOGLE_API_KEY")
except UndefinedValueError:
    GOOGLE_API_KEY = ""

if not GOOGLE_API_KEY:
    GOOGLE_API_KEY = ""
    print("no google api key file found.")

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')
MEDIA_DIR = os.path.join(BASE_DIR, 'media')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
try:
    SECRET_KEY = config('SECRET_KEY')
except UndefinedValueError:
    SECRET_KEY = "fdsgfsdf3erdewf232343242fw#ERD$#F#$F$#DD"

# SECURITY WARNING: don't run with debug turned on in production!

# If in production mode, turn off debugging
if PRODUCTION_SERVER and not DEBUG_ON:
    DEBUG = False
else:
    DEBUG = True

ALLOWED_HOSTS = local_conf.ALLOWED_HOSTS

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = 'accounts/login/'

# Application definition
INSTALLED_APPS = [
                     'django.contrib.admin',
                     'django.contrib.auth',
                     'django.contrib.contenttypes',
                     'django.contrib.sessions',
                     'django.contrib.messages',
                     'django.contrib.staticfiles',
                     'django.contrib.humanize',
                     'bootstrap4',
                     'el_pagination',
                     'easy_pdf',
                     'tracking',
                     'accounts',
                     'lib',
                     'shared_models',
                     'tickets',
                 ] + local_conf.MY_INSTALLED_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'tracking.middleware.VisitorTrackingMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'dm_apps.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'dm_apps.context_processor.my_envr'
            ],
        },
    },
]

WSGI_APPLICATION = 'dm_apps.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

# DATABASE_ROUTERS = ['dm_apps.routers.WhaleDatabaseRouter', ]
DATABASES = local_conf.DATABASES

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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

# Email settings

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
# EMAIL_PORT = 587
EMAIL_PORT = 25
EMAIL_USE_TLS = False

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Halifax'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

LANGUAGES = [
    ('en', _('English')),
    ('fr', _('French')),
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/
MEDIA_ROOT = MEDIA_DIR
MEDIA_URL = '/media/'

STATIC_URL = '/static/'
# STATIC_ROOT = STATIC_DIR

if PRODUCTION_SERVER:
    STATIC_ROOT = STATIC_DIR
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

else:
    STATICFILES_DIRS = [
        STATIC_DIR,
    ]

# This setting should allow for submitting forms with lots of fields. This is especially relevent when using formsets as in ihub > settings > orgs...
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000

# Setting for django-tracking2
TRACK_PAGEVIEWS = True
TRACK_QUERY_STRING = True
TRACK_REFERER = True
TRACK_SUPERUSERS = False
