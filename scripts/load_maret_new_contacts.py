import os
import json

from django.contrib.auth.models import User
from masterlist.models import Person
from django.core import serializers

input_path = r'c:\Users\upsonp\Downloads\maret_contacts.json'

file = open(input_path, 'r')
jfile = json.load(file)

output_path = r'c:\Users\upsonp\Downloads\maret_contacts_2.json'

me = User.objects.get(username='patrick.upson@dfo-mpo.gc.ca')
id_array = []
for obj in jfile:
    fields = obj['fields']
    if len(Person.objects.filter(first_name=fields['first_name'], last_name=fields['last_name'])) <= 0:
        person = Person(designation=fields['designation'], first_name=fields['first_name'], last_name=fields['last_name'],
                        phone_1=fields['phone_1'], email_1=fields['email_1'],
                        language=fields['language'], notes=fields['notes'],
                        locked_by_ihub=fields['locked_by_ihub'],
                        date_last_modified=fields['date_last_modified'], last_modified_by=me)
        person.save()
        id_array.append(person.pk)
    else:
        person = Person.objects.get(first_name=fields['first_name'], last_name=fields['last_name'])
        id_array.append(person.pk)
        print("{} {} already exists".format(fields['first_name'], fields['last_name']))

""" a simple function to export the important lookup tables. These fixtures will be used for testing and also for
seeding new instances"""
if not output_path:
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')

if not os.path.isdir(output_path):
    os.mkdir(output_path)

data = serializers.serialize("json", Person.objects.filter(pk__in=id_array))
parsed = json.loads(data)
my_label = Person._meta.db_table
f = open(os.path.join(output_path, f'{my_label}.json'), 'w', encoding='utf-8')
f.write(json.dumps(parsed, indent=4, sort_keys=True))
f.close()
