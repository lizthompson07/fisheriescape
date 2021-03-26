import os
from django.core import management

# fixture file directory to get files from
fixture_dir = r'csas/fixtures/csas_requests/'

# scan the directory for files (assume files are all .json files) and store the found files in an array
files = [f for f in os.listdir(fixture_dir) if os.path.isfile(os.path.join(fixture_dir, f))]

# iterate over the array of files and load each using the django management.call_command function
for file in files:
    management.call_command('loaddata', os.path.join(fixture_dir, file))