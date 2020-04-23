#!/bin/bash
echo "\n\nRUNNING TESTS FOR: shared_models app"
python manage.py test --keepdb shared_models.test

echo "\n\nRUNNING TESTS FOR: projects app"
python manage.py test --keepdb projects.test

echo "\n\nRUNNING TESTS FOR: travel app"
python manage.py test --keepdb travel.test

echo "\n\nRUNNING TESTS FOR: whalesdb"
python manage.py test --keepdb whalesdb.test

echo "\n\nRUNNING TESTS FOR: inventory"
python manage.py test --keepdb inventory.test
