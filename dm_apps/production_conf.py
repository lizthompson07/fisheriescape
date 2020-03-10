# INSTRUCTIONS:  #
##################
# please refer to the README and the project wiki for the most up-to-update information.
# Duplicate this file and rename it to my_conf.py
# The 'my_conf.py' file is in the .gitignore
# As this file in a part of the repository, please do not make any customizations here

import os
from decouple import config
from .utils import is_db_connection_available, get_db_connection_dict

# DO NOT INTERACT WITH THESE VARIABLES HERE
########################################################################
DEV_DB_NAME = None
DEV_DB_HOST = None
USING_LOCAL_DB = False
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
########################################################################

# Should Microsoft Azure AD be used for authentication? By default, if a file called `azure_oauth_settings.yml' is in the root dir, azure aad will be turned on
# this is a manual override. Uncomment to turn off AAD regardless of the presence of the above mentioned file.
# AZURE_AD = False

# Should the ticketing app be displayed on the main index page?
SHOW_TICKETING_APP = True

# Should DEBUG mode be turned on? Uncomment the line below to turn on debugging
# DEBUG = True

# To add any custom hosts to this application's list of allowed hosts, provide them here
ALLOWED_HOSTS_TO_ADD = []

# Specify the full url of the site. This is used in email templates to link the recipient back to the site; NO TRAILING SLASH!!
SITE_FULL_URL = "https://dmapps-test-web.azurewebsites.net"


# If the line below is set to True, you will connect to the dev database, provided that DEV db connection information is
# available in environmental variables, e.g. 'DEV_DB_HOST', 'DEV_DB_PASSWORD', ... (see .env_sample)
# If this is set to False, the application will defer to the 'DB_TYPE' env var to determine what type of database it is connecting to
FORCE_DEV_DB = False

# add new applications to this dictionary; grey out any app you do not want
# the dict key should be the actual name of the app
# if there is a verbose name, it should be the key value, otherwise None
APP_DICT = {
    #'inventory': 'Metadata Inventory',
    #'grais': 'grAIS',
    #'oceanography': 'Oceanography',
    #'herring': 'HerMorrhage',
    #'camp': 'CAMP db',
    #'meq': 'Marine environmental quality (MEQ)',
    #'diets': 'Marine diets',
    #'projects': 'Science project planning',
    #'ihub': 'iHub',  # dependency on masterlist
    #'scifi': 'SciFi',
    #'masterlist': 'Masterlist',
    #'shares': 'Gulf Shares',
    'travel': 'Travel Management System',
    #'sar_search': "SAR Search",
    #'spot': 'Grants & Contributions (Spot)',  # dependency on masterlist, sar_search
    #'ios2': 'Instruments',
    #'staff': "Staff Planning Tool",
    #'publications': "Project Publications Inventory",
    #'trapnet': "TrapNet",
    #'whalesdb': "Whale Equipment Deployment Inventory",
    #'vault': "Marine Megafauna Media Vault",
}

MY_INSTALLED_APPS = [app for app in APP_DICT]

# check to see if the databases connection information is available in environmental variables:
if FORCE_DEV_DB and is_db_connection_available(dev=True):
    db_dict = get_db_connection_dict(dev=True)
    DB_MODE = "DEV"
    if is_db_connection_available() and get_db_connection_dict()["DB_MODE"].upper() == "PROD":
        print("production db connection string present however running dev mode since FORCE_DEV_MODE setting is set to True")
    # if we have a connection, get the names of db and host to pass in as context processors
    DB_NAME = db_dict["DB_NAME"].upper()
    DB_HOST = db_dict["DB_HOST"].upper()

# if not, check to see if general database information was provided
elif is_db_connection_available():
    if FORCE_DEV_DB:
        print("FORCE_DEV_MODE setting is set to True, however could not find dev DB connection information")
    db_dict = get_db_connection_dict()
    DB_MODE = db_dict["DB_MODE"].upper()

    # if we have a connection, get the names of db and host to pass in as context processors
    DB_NAME = db_dict["DB_NAME"].upper()
    DB_HOST = db_dict["DB_HOST"].upper()

#  otherwise we are using a local sqlite version
else:
    USING_LOCAL_DB = True
    DB_MODE = "DEV"
    DB_NAME = "db.sqlite3"
    DB_HOST = "local"


# Specify your database connection details
if USING_LOCAL_DB:
    print("No database connection information found in environmental variables. Using local Sqlite db")
    my_default_db = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
else:
    my_default_db = {
        'ENGINE': 'django.db.backends.mysql',
        'TIME_ZONE': 'America/Halifax',
        'OPTIONS': {
            'host': db_dict["DB_HOST"],
            'port': db_dict["DB_PORT"],
            'database': db_dict["DB_NAME"],
            'user': db_dict["DB_USER"],
            'password': db_dict["DB_PASSWORD"],
            'init_command': 'SET default_storage_engine=INNODB',
        }}

DATABASES = {
    'default': my_default_db,
}
