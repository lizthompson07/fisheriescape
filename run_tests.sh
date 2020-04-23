echo "running testing for shared_models app"
python manage.py test --keepdb shared_models.test

echo "running testing for projects app"
python manage.py test --keepdb projects.test

echo "running testing for travel app"
python manage.py test --keepdb travel.test

echo "running tests for whalesdb"
python manage.py test --keepdb whalesdb.test

echo "running tests for inventory app"
python manage.py test --keepdb inventory
