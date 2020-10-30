:: testing for shared_models app
python manage.py test -b shared_models.test --keepdb

:: testing for projects app
python manage.py test -b projects.test --keepdb

:: testing for travel app
python manage.py test -b travel.test --keepdb

:: run tests for whalesdb app
python manage.py test -b whalesdb.test --keepdb

:: run tests for inventory app
python manage.py test -b inventory.test --keepdb

:: run tests for shiny
python manage.py test -b shiny.test --keepdb

:: run tests for ihub
python manage.py test -b ihub.test --keepdb

:: run tests for csas
python manage.py test -b csas.test --keepdb

:: run tests for cruises
python manage.py test -b cruises.test --keepdb