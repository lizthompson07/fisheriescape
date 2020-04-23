#!/bin/bash
echo "RUNNING TESTS FOR: shared_models app"
python manage.py test --keepdb shared_models.test

echo "RUNNING TESTS FOR: projects app"
mkdir ./media
mkdir ./media/projects
mkdir ./media/projects/temp
python manage.py test --keepdb projects.test

echo "RUNNING TESTS FOR: travel app"
python manage.py test --keepdb travel.test

echo "RUNNING TESTS FOR: whalesdb"
python manage.py test --keepdb whalesdb.test

echo "RUNNING TESTS FOR: inventory"
python manage.py test --keepdb inventory.test
