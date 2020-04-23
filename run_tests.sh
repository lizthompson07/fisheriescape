#!/bin/bash
echo "\n"
echo "RUNNING TESTS FOR: shared_models app"
python manage.py test --keepdb shared_models.test

echo "\n"
echo "RUNNING TESTS FOR: projects app"
mkdir ./media
mkdir ./media/projects
mkdir ./media/projects/temp
python manage.py test --keepdb projects.test

echo "\n"
echo "RUNNING TESTS FOR: travel app"
python manage.py test --keepdb travel.test

echo "\n"
echo "RUNNING TESTS FOR: whalesdb"
python manage.py test --keepdb whalesdb.test

echo "\n"
echo "RUNNING TESTS FOR: inventory"
python manage.py test --keepdb inventory.test

echo "\n"
echo "RUNNING TESTS FOR: shiny"
python manage.py test --keepdb shiny.test
