## Repository for the DFO Science Data Management Website (formally Gulf Science Data Management Website)

### Prerequisite to running the application
1. Install Python 3 (<https://www.python.org>), and make sure that Python is added to your PATH variable.
1. Working from your root projects directory (e.g., `~/my_projects`), create python virtual environment: `python -m venv dfo_sci_dm_site_venv`
1. Activate the virtual environment, (Windows): `.\dfo_sci_dm_site_venv\Scripts\activate` (Linux): `source ./dfo_sci_dm_site_venv/bin/activate`
1. Clone project: `git clone https://github.com/dfo-mar-odis/dfo_sci_dm_site`
1. navigate into the project director: `cd dfo_sci_dm_site`
1. Try installing the Python virtual environment libraries required by the application: `pip install -r stable_reqs.txt`.
1. **If the previous step worked, skip this step.** 
If you do not have C development tools installed on your machine, the `mysqlclient` cannot be installed and the package installation procedure above will fail. 
In order to proceed it, you will need to install the `mysqlclient` prerequisites (not covered here) or download the precompiled version of the library:
    - copy `stable_reqs.txt` to `my_stable_reqs.txt`, (Windows): `copy .\stable_reqs.txt .\my_stable_reqs.txt` (Linux): `cp ./stable_reqs.txt ./my_stable_reqs.txt`
    - copy `stable_reqs.txt` to `my_stable_reqs.txt`, (Windows): `copy .\stable_reqs.txt .\my_stable_reqs.txt` (Linux): `cp ./stable_reqs.txt ./my_stable_reqs.txt`
    - open `my_stable_reqs.txt` and comment out or remove `mysqlclient==1.3.12`
    - re-attempt to install libraries: `pip install -r my_stable_reqs.txt`. You should get no errors this time.
    - Download the binary `mysqlclient` [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#mysqlclient). Be sure to select the file that matches your system configuration. For example, if your a running python 3.6 on an AMD64 processor, you would download the file called `mysqlclient‑1.x.x‑cp36‑cp36m‑win_amd64.whl.` Install the local file: `pip install /path/to/local/file/mysqlclient‑1.x.x‑cp36‑cp36m‑win_amd64.whl`

### Running the django development server
1. Change directory to the root `dfo_sci_dm_site` folder (if not already there) and run the development server: `python manage.py runserver`

### Notes
- Without any additional configuration, the app will connect to the Gulf Region's development database called [glf_sci_site_dev] (see file `dev.cnf` for database connection details)
- The development server is essentially a slave of the production database. There is currently no script to automate the syncing 
so it will be done on an as needed basis. **The development database is overwritten each time it is synced with the production database.** 
- For more elaborate details about getting setup, please visit the site's [wiki](https://github.com/dfo-mar-odis/dfo_sci_dm_site/wiki).