# INSTRUCTIONS:  #
##################

# Duplicate this file and rename it to my_conf.py
# The 'my_conf.py' file is in the .gitignore
# create a file called prod.cnf in the root project dir to specify connection to production db server
# The 'prod.cnf' file is also in the .gitignore
# It is recommended to leave this file unmodified unless you are making improvements

import os

# DO NOT CHANGE THESE VARIABLES
FORCE_DEV_DB = False
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# This is the name of the production database connection file; if missing, we will use dev.cnf with is included in the repo
MY_CNF = os.path.join(BASE_DIR, 'prod.cnf')
# uncomment this line if you want to connect to the production database instead of the default dev database (assuming prod.cnf is present)
FORCE_DEV_DB = True

# checking to see if the which database to connect to:
# if prod.cnf exists and we are not forcing dev mode...
if os.path.isfile(MY_CNF) and not FORCE_DEV_DB:
    USING_PRODUCTION_DB = True
# otherwise we are in dev mode
else:
    if os.path.isfile(MY_CNF):
        print("production connection string is present however running dev mode since FORCE_DEV_MODE setting is set to True")
    MY_CNF = os.path.join(BASE_DIR, 'dev.cnf')
    # this variable is used in base.html to indicate which database you are connected to
    USING_PRODUCTION_DB = False

# Specific which mode you are running in. If this file is on the production server, this setting should be True
# if this setting = False, static and mediafiles will be served by the development server.
PRODUCTION_SERVER = False

# this property is only looked at if PRODUCTION_SERVER = True. By setting DEBUG = True, you will override the default programming to set
# DEBUG = False when using a prod server
DEBUG = True

# add your hostname here.
ALLOWED_HOSTS = ['127.0.0.1', ]

# add new applications to this dictionary; grey out any app you do not want
# the dict key should be the actual name of the app
# if there is a verbose name, it should be the key value, otherwise None
APP_DICT = {
    'inventory': 'Metadata Inventory',
    'grais': 'grAIS',
    'oceanography': 'Oceanography',
    'herring': 'HerMorrhage',
    'camp': 'CAMP db',
    'meq': 'Marine environmental quality (MEQ)',
    'diets': 'Marine diets',
    'projects': 'Science project planning',
    'ihub': 'iHub',  # dependency on masterlist
    'scifi': 'SciFi',
    'masterlist': 'Masterlist',
    'shares': 'Gulf Shares',
    'travel': 'Travel Management System',
    'sar_search': "SAR Search",
    'spot': 'G&C App (Spot)',  # dependency on sar_search, masterlist
    'publications': 'Project Publications Inventory',
    'ios2': 'Instruments',
    'staff': "Staff Planning Tool",
    'trapnet': "TrapNet",
    'whalesdb': "Whale Equipment Deployment Inventory",
}

MY_INSTALLED_APPS = [app for app in APP_DICT]
SHOW_TICKETS_APP = True

# Specify your database connection details
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'TIME_ZONE': 'America/Halifax',
        'OPTIONS': {
            'read_default_file': MY_CNF,
            'init_command': 'SET default_storage_engine=INNODB',
        },
    },
    # 'whalesdb': {
    #     #     'ENGINE': 'django.db.backends.oracle',
    #     #     'NAME': 'DTRAN',
    #     #     'USER': 'whale_amd',
    #     #     'PASSWORD': 'BigSpla3h#',
    #     #     'HOST': 'VSNSBIOD78.ENT.DFO-MPO.CA',
    #     #     'PORT': '1521'
    #     # },
    # 'whalesdb': {
    #     'ENGINE': 'django.db.backends.oracle',
    #     'NAME': 'TTRAN',
    #     'USER': 'whale_amd',
    #     'PASSWORD': 'BigSpla3h2#',
    #     'HOST': 'VSNSBIOD78.ENT.DFO-MPO.CA',
    #     'PORT': '1521'
    # },
}

# this is for pycharm
WEB_APP_NAME = "DMApps"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')
MEDIA_DIR = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
from django.utils.translation import gettext_lazy as _

# Quick-start development set
SECRET_KEY = 'dekdlvbhtlbo_wg_x32ovt9umh3ysbfa$+f@h7i8oe-45$c)pl'
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
    'accounts',
    'lib',
    'shared_models',
    'tickets',
    'inventory',
    'grais',
    'oceanography',
    'herring',
    'camp',
    'meq',
    'diets',
    'projects',
    'ihub',
    'scifi',
    'masterlist',
    'shares',
    'travel',
    'spot',
    'ios2',
    'trapnet',
    'tracking',
    'sar_search',
]

ROOT_URLCONF = 'dm_apps.urls'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'tracking.middleware.VisitorTrackingMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

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

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    STATIC_DIR,
]
