## Repository for the Gulf Science Data Management Website

### Prerequisite to running the application
1. Install Python (<https://www.python.org>), and make sure that Python is added to your PATH variable.

2. Create a Python virtual environment and activate it. 
To do so, create a directory on your computer where the virtual environment will live 
(called VENV-FOLDER in the example below), 
create the virtual environment in that directory and activate the virtual environment:

```
python -m venv glf_sci_site_venv
```
To activate the venv on windows:
```
.\glf_sci_site_venv\Scripts\activate
```
To activate the venv on linux:
```
source .\glf_sci_site_venv\bin\activate
```

3. Clone the glf_sci_site repository

4. Install the Python packages required by the glf_sci_site application
```
pip install -r stable_reqs.txt
```

### Running the server application
1. Change directory to the root glf_sci_site folder and run the server application
```
python manage.py runserver
```

- Without any other configuration, the app will connect to the development database
- The development server is essentially a slave of the production database. There is currently no script to automate the syncing 
so it will be done on an as needed basis