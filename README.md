# Fisheriescape

# Local Setup
## Prerequisites
1. PSQL server running
2. Redis server running
3. Python 3.9: https://www.python.org/downloads/release/python-3916/
4. GDAL installed: https://gdal.org/download.html
5. PROJ installed: https://proj.org/install.html
6. postgis installed: https://postgis.net/install/

## Config
1. Copy `.env_sample` and rename it to `.env`
2. Update the env variables to match your local config
3. Copy `my_conf_sample.py` and rename it to `my_conf.py`

## Setup local DB
Install PSQL spatial extension
https://docs.djangoproject.com/fr/3.2/ref/contrib/gis/install/postgis/

### Create DB
```bash
psql postgres
```
### Setup DB user:
```sql
\c fisheriescape
```
```sql
CREATE USER localuser WITH PASSWORD 'localpassword';
ALTER ROLE localuser SET client_encoding TO 'utf8';
ALTER ROLE localuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE localuser SET timezone TO 'UTC';
```

### Grant privileges to local DB user:
```sql
GRANT ALL PRIVILEGES ON DATABASE fisheriescape TO localuser;
ALTER ROLE localuser SUPERUSER;
```
### Quit the psql prompt
```sql
\q
```

## Setup local env
1. Create a virtual environment
   at `/fisheriescape`
   ```bash
   python3.9 -m venv venv
   ```
2. Activate the virtual environment
   ```bash
   source venv/bin/activate
   ```
3. Install dependencies
    ```bash
   pip install -r requirements.txt
   ```
4. Run the unit tests to make sure everything is setup properly
   

## Import local data
1. Import test data to your local DB
   1. Get the fixtures.zip file and unzip it somewhere on your local computer. Write down the folder path
   2. Load the fixtures
      ```bash
      python manage.py loaddata [absolute\path\to\fixtures\folder]\*.json
      ```
2. Import Score and Vulnerable Species data to your local DB
   1. Run the app : `python manage.py runserver`
   2. Navigate to http://127.0.0.1:8000/ and login using the email `admin_test_user@dfo-mpo.gc.ca`. 
   The magic link to login will appear in the terminal where Django is running.
   3. Navigate to http://127.0.0.1:8000/fr/fisheriescape/import/fisheriescape-scores
   4. Upload Vulnerable Species files
   5. Navigate to http://127.0.0.1:8000/fr/fisheriescape/import/vulnerable-species-spots
   6. Upload Scores files

   > Species and vulnerable species will be created automatically, based on the names present in the files imported

## Getting Started with this Project for Development
Before proceeding any further, make sure you have completed the steps outlined above.

### Static files
Static files are not stored in the git repository, they can be pushed to the static file server using `python manage.py findstatic` and downloaded to a machine for local development using `python manage.py collectstatic`. If this step is skipped the "you are not using chrome" warning message will show and images will appear broken on the "127.0.0.1:8000/en" page

**The first step of customizing the site's configuration is by cloning the `.env_sample` file and renaming this copy to `.env`.** This file is also in the .gitignore.
This file has numerous switches and flags that can be used for customizing the application. The `.env_sample` file has a lot of annotation and the configuration 
settings should be fairly straight-forward. If you find any of them confusing, please open an issuein the `dmapps` repo. 

Most types of customizations can be done through the `.env` file. However, changes made to which apps are switched on/off or which type of database backend you want to 
use must be done in a separate file. **To do these types of customization, make a copy of the file called `./dm_apps/default_conf.py` to `./dm_apps/my_conf.py`.**
The latter file is in the .gitignore therefore none of the changes made will be recorded to the repo. If the `my_conf.py` file is present when the 
application boots up, the `default_conf.py` file will be ignored and the application will look to the `my_conf` file. At this point you would be free
to make any changes you like to the `my_conf`. 


**Important:** You should not be making changes to the `.env_sample` and/or `default_conf.py` unless these are changes that are meant to be 
persisted in the repository for all users. For example, if you were working on a new app, you would eventually have to modify the `default_conf`.   

### Connecting existing apps to an instance
Apps can be easily connected and disconnected from an instance of the application. To do so, you simply comment / uncomment
the app of interest in the app dictionary: `my_conf.APP_DICT`. Each connected app should have a card display on the site's main index page.


## Collaborative workflow
1. If you are reading this, your contributions and collaborations are welcomed :)
1. Please do your work locally and make sure to pull regularly from `origin/master`
1. When ready to merge your work, please be sure to run the project's unit tests before creating your merge request
    1. if you are using windows, you can run the suite of test using the following batch file: `run_tests_in_windows.bat`
1. Please do not create a merge request that has conflicts with the master branch, unless you specifically need help with dealing with any conflicting code.
    1. in the case of the latter, please be sure to properly assign your merge request and add the appropriate comments
