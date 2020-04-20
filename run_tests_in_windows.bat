:: testing for shared_models app
python manage.py test shared_models.test --keepdb

:: testing for projects app
python manage.py test projects.test --keepdb

:: testing for travel app
python manage.py test travel.test --keepdb

:: run tests for whalesdb app
python manage.py test whalesdb.test --keepdb