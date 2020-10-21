#!/bin/bash
printf "\n"
echo "RUNNING TESTS FOR: shared_models app"
python3.8 manage.py test  shared_models.test

printf "\n"
echo "RUNNING TESTS FOR: projects app"
mkdir ./media
mkdir ./media/projects
mkdir ./media/projects/temp
python3.8 manage.py test projects.test

printf "\n"
echo "RUNNING TESTS FOR: travel app"
python3.8 manage.py test travel.test

printf "\n"
echo "RUNNING TESTS FOR: whalesdb"
python3.8 manage.py test whalesdb.test

printf "\n"
echo "RUNNING TESTS FOR: inventory"
python3.8 manage.py test inventory.test

printf "\n"
echo "RUNNING TESTS FOR: shiny"
python3.8 manage.py test shiny.test

printf "\n"
echo "RUNNING TESTS FOR: ihub"
python3.8 manage.py test ihub.test

printf "\n"
echo "RUNNING TESTS FOR: csas"
python3.8 manage.py test csas.test