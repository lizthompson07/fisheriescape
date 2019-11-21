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
DEBUG = False

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
    'spot': 'Grants & Contributions (Spot)',  # dependency on masterlist, sar_search
    'ios2': 'Instruments',
    'staff': "Staff Planning Tool",
    'publications': "Project Publications Inventory",
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
    #     'ENGINE': 'django.db.backends.oracle',
    #     'NAME': 'DTRAN',
    #     'USER': 'whale_amd',
    #     'PASSWORD': 'BigSpla3h#',
    #     'HOST': 'VSNSBIOD78.ENT.DFO-MPO.CA',
    #     'PORT': '1521'
    # },
}