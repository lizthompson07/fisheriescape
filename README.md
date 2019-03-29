## Repository for the Gulf Science Data Management Website

### Prerequisite to running the application
1. Install Python (<https://www.python.org>), and make sure that Python is added to your PATH variable.
1. Create a Python virtual environment and activate it. 
To do so, create a directory on your computer where the virtual environment will live 
(called 'glf_sci_site_venv' in the example below), 
create the virtual environment in that directory and activate the virtual environment:
    1. To activate the venv on windows: `python -m venv glf_sci_site_venv`
    1. To activate the venv on linux: `source .\glf_sci_site_venv\bin\activate`
1. Clone the glf_sci_site repository
```
git clone https://github.com/dfo-mar-odis/dfo_sci_dm_site
```
1. Install the Python packages required by the glf_sci_site application
```
pip install -r stable_reqs.txt
```

### important note about installing mysqlclient
you might need to download the precompiled version of mysqlclient. If you need to do this, you will need to download the binary
file and remove the mysqlclient line from the stable_reqs.txt file. The binary file can be downloaded 
[here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#mysqlclient). Be sure to select the file that matches your system configuration.
For example, if your a running python 3.6 on an AMD64 processor, you would download the file called 
'mysqlclient‑1.x.x‑cp36‑cp36m‑win_amd64.whl.' To install a local wheel:
```
pip install /path/to/local/file/mysqlclient‑1.x.x‑cp36‑cp36m‑win_amd64.whl
```

### Running the server application
1. Change directory to the root glf_sci_site folder and run the server application
```
python manage.py runserver
```
- Without any other configuration, the app will connect to the development database
- The development server is essentially a slave of the production database. There is currently no script to automate the syncing 
so it will be done on an as needed basis