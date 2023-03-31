# INSTRUCTIONS:  #
##################
# please refer to the README and the project wiki for the most up-to-update information.
# If you want to customize this app, duplicate this file and rename it to my_conf.py and make changes
# through that file. The 'my_conf.py' file is in the .gitignore
# As this file in a part of the repository, please do not make any customizations here

import os

from .utils import db_connection_values_exist, get_db_connection_dict

########
# APPS #
########

# add new applications to this dictionary; grey out any app you do not want
# the dict key should be the actual name of the app
# if there is a verbose name, it should be the value of key 'name', otherwise None

APP_DICT = {
    'fisheriescape': dict(name="Fisheries Landscape Tool"),
}




MY_INSTALLED_APPS = [app for app in APP_DICT]

#############
# DATABASES #
#############

# By default, the application will use the setting from the environment variables (or .env file).
# If those variables are not set, the local db will be created. If you would like to use a local db
# disrespective of the environment variables, set it to True
USE_LOCAL_DB = False

# get the connection information from the env; if not all values present, default to local db
db_connections = get_db_connection_dict()
if not db_connection_values_exist(db_connections):
    USE_LOCAL_DB = True
    print("DB connection values are not specified. Can not connect to the database. Connecting to local db instead.")
else:
    print(f" *** Connecting to database '{db_connections['DB_NAME'].upper()}' on host '{db_connections['DB_HOST'].upper()}' ***")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

my_default_db = {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'HOST': db_connections["DB_HOST"],
        'PORT': db_connections["DB_PORT"],
        'NAME': db_connections["DB_NAME"],
        'USER': db_connections["DB_USER"],
        'PASSWORD': db_connections["DB_PASSWORD"],
        'INIT_COMMAND': 'SET default_storage_engine=INNODB',
    }

# if we have a connection, get the names of db and host to pass in as context processors
DB_NAME = db_connections["DB_NAME"]
DB_HOST = db_connections["DB_HOST"]

# give the user an option to not define the db mode. If not provided, it will be guessed at from the host name
if not db_connections["DB_MODE"]:
    # Determine which DB we are using from the host name"
    if "dmapps-dev-db" in db_connections["DB_HOST"] and db_connections["DB_NAME"] == "dmapps":
        DB_MODE = "DEV"
    elif "dmapps-dev-db" in db_connections["DB_HOST"] and db_connections["DB_NAME"] == "dmapps-test":
        DB_MODE = "TEST"
    elif "dmapps-prod-db" in db_connections["DB_HOST"]:
        DB_MODE = "PROD"
else:
    DB_MODE = db_connections["DB_MODE"]

DATABASES = {
    'default': my_default_db,
}

#############
# CACHES    #
#############

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        # 'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        'LOCATION': 'cache',
    }
}
