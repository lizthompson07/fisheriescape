#!/bin/bash
printf "\n"
echo "RUNNING TESTS FOR: shared_models app"
python3.8 manage.py test -b  shared_models.test
echo "FINISHED RUNNING TESTS FOR: shared_models app"

printf "\n"
printf "\n"
printf "#############################################################################################################################"
printf "\n"
printf "\n"
echo "RUNNING TESTS FOR: projects app"
mkdir ./media
mkdir ./media/projects
mkdir ./media/projects/temp
python3.8 manage.py test -b projects.test
echo "FINISHED RUNNING TESTS FOR: projects app"

printf "\n"
printf "\n"
printf "#############################################################################################################################"
printf "\n"
printf "\n"
echo "RUNNING TESTS FOR: travel app"
python3.8 manage.py test -b travel.test

printf "\n"
printf "\n"
printf "#############################################################################################################################"
printf "\n"
printf "\n"
echo "RUNNING TESTS FOR: whalesdb"
python3.8 manage.py test -b whalesdb.test
echo "FINISHED RUNNING TESTS FOR: whalesdb"

printf "\n"
printf "\n"
printf "#############################################################################################################################"
printf "\n"
printf "\n"
echo "RUNNING TESTS FOR: inventory"
python3.8 manage.py test -b inventory.test
echo "FINISHED RUNNING TESTS FOR: inventory"

printf "\n"
printf "\n"
printf "#############################################################################################################################"
printf "\n"
printf "\n"
echo "RUNNING TESTS FOR: shiny"
python3.8 manage.py test -b shiny.test
echo "FINISHED RUNNING TESTS FOR: shiny"

printf "\n"
printf "\n"
printf "#############################################################################################################################"
printf "\n"
printf "\n"
echo "RUNNING TESTS FOR: ihub"
python3.8 manage.py test -b ihub.test
echo "FINISHED RUNNING TESTS FOR: ihub"

printf "\n"
printf "\n"
printf "#############################################################################################################################"
printf "\n"
printf "\n"
echo "RUNNING TESTS FOR: csas"
python3.8 manage.py test -b csas.test
echo "FINISHED RUNNING TESTS FOR: csas"

printf "\n"
printf "\n"
printf "#############################################################################################################################"
printf "\n"
printf "\n"
echo "RUNNING TESTS FOR: cruises"
python3.8 manage.py test -b cruises.test
echo "FINISHED RUNNING TESTS FOR: cruises"
