# INSTRUCTIONS:  #
##################
# please refer to the README and the project wiki for the most up-to-update information.
# Duplicate this file and rename it to my_conf.py
# The 'my_conf.py' file is in the .gitignore
# As this file in a part of the repository, please do not make any customizations here

import os
from decouple import config
from .utils import db_connection_values_exist, get_db_connection_dict



# Should Microsoft Azure AD be used for authentication? By default, if a file called `azure_oauth_settings.yml' is in the root dir, azure aad will be turned on
# this is a manual override. Uncomment to turn off AAD regardless of the presence of the above mentioned file.
# AZURE_AD = False

# Should the ticketing app be displayed on the main index page?
SHOW_TICKETING_APP = True

# Should DEBUG mode be turned on? Uncomment the line below to turn on debugging
# DEBUG = True

# To add any custom hosts to this application's list of allowed hosts, provide them here
ALLOWED_HOSTS_TO_ADD = []


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
    'vault': "Marine Megafauna Media Vault",
}

# By default, the application will use the setting from the environment variables (or .env file).
# If those variables are not set, the local db will be created. If you would like to use a local db
# disrespective of the environment variables, set it to True
USE_LOCAL_DB = False


###
### Do not change below
###

DEPLOYMENT_STAGE = config('DEPLOYMENT_STAGE').upper()

# This is used in email templates to link the recipient back to the site
#TODO: Some basic checks for format?
SITE_FULL_URL = config('SITE_FULL_URL')


db_connections = get_db_connection_dict()


### Deploying application in production - don't change, unless you know what you're doing
if DEPLOYMENT_STAGE == 'PROD': 
    AZURE_AD = True
    USE_LOCAL_DB = False
    ALLOWED_HOSTS_TO_ADD = []
    APP_DICT = {
        'travel': 'Travel Management System'
    }

    

### Deploying application in test environment 
elif DEPLOYMENT_STAGE == 'TEST':
    AZURE_AD = True
    USE_LOCAL_DB = False
    ALLOWED_HOSTS_TO_ADD = []
    APP_DICT = {
        'travel': 'Travel Management System'
    }


### Deploying application in dev environment 
elif DEPLOYMENT_STAGE == 'DEV':
    AZURE_AD = True
    USE_LOCAL_DB = False
    ALLOWED_HOSTS_TO_ADD = []


### Deploying application on your local machine 
else:  
    if not db_connection_values_exist(db_connections):
        print("No connection vars specified - creating local db.")
        USE_LOCAL_DB = True

    ## I.e. if db connection is specified in env variables or .env file, then the new sqlite db would not be used

    


MY_INSTALLED_APPS = [app for app in APP_DICT]



if USE_LOCAL_DB:
    my_default_db = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
    #TODO: David, since "DEV" is also database in the DEV stage environment, 
    # should this be "LOCAL" and => another color in the context processor???
    DB_MODE = "DEV"  ## LOCAL
    DB_NAME = "db.sqlite3"
    DB_HOST = "local"
else:
    if not db_connection_values_exist(db_connections):
        raise Exception("DB connection values are not specifid. Can not connect to the dabase.")

    my_default_db = {
        'ENGINE': 'django.db.backends.mysql',
        'TIME_ZONE': 'America/Halifax',
        'OPTIONS': {
            'host': db_connections["DB_HOST"],
            'port': db_connections["DB_PORT"],
            'database': db_connections["DB_NAME"],
            'user': db_connections["DB_USER"],
            'password': db_connections["DB_PASSWORD"],
            'init_command': 'SET default_storage_engine=INNODB',
        }}

    # if we have a connection, get the names of db and host to pass in as context processors
    DB_NAME = db_connections["DB_NAME"]
    DB_HOST = db_connections["DB_HOST"]

    # Determine which DB we are using from the host name"
    if "dmapps-dev-db" in db_connections["DB_HOST"] and db_connections["DB_NAME"] == "dmapps":
        DB_MODE = "DEV"
    elif  "dmapps-dev-db" in db_connections["DB_HOST"] and db_connections["DB_NAME"] == "dmapps-test":
        DB_MODE = "TEST"
    elif  "dmapps-prod-db" in db_connections["DB_HOST"] :
        DB_MODE = "PROD"

DATABASES = {
    'default': my_default_db,
}