## Repository for the Gulf Science Data Management Website

### Prerequisite to running the application
1. Install Python (<https://www.python.org>), and make sure that Python is added to your PATH variable.

2. Create a Python virtual environment and activate it. To do so, create a directory on your computer where the virtual environment will live (called VENV-FOLDER in the example below), create the virtual environment in that directory and activate the virtual environment:
```
python -m venv VENV-FOLDER
cd VENV-FOLDER
activate
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

Without any other configuration, the app will connect to the development database
