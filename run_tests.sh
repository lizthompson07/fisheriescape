#!/bin/bash
printf "\n"
echo "RUNNING TESTS FOR: shared_models app"
python manage.py test  shared_models.test

printf "\n"
echo "RUNNING TESTS FOR: projects app"
mkdir ./media
mkdir ./media/projects
mkdir ./media/projects/temp
python manage.py test projects.test

printf "\n"
echo "RUNNING TESTS FOR: travel app"
python manage.py test travel.test

printf "\n"
echo "RUNNING TESTS FOR: whalesdb"
python manage.py test whalesdb.test

printf "\n"
echo "RUNNING TESTS FOR: inventory"
python manage.py test inventory.test

printf "\n"
echo "RUNNING TESTS FOR: shiny"
python manage.py test shiny.test

printf "\n"
echo "RUNNING TESTS FOR: ihub"
python manage.py test ihub.test

printf "\n"
echo "RUNNING TESTS FOR: csas"
python manage.py test csas.test