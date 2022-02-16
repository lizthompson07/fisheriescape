import os
import json

from django.contrib.auth.models import User
from masterlist.models import Organization
from shared_models.models import Province
from django.core import serializers

file_loc = r'c:\Users\upsonp\Downloads\fixture_4_Organization_List_v2.json'

file = open(file_loc, 'r')
jfile = json.load(file)

output_path = r'c:\Users\upsonp\Downloads\maret_organization.json'

me = User.objects.get(username='patrick.upson@dfo-mpo.gc.ca')
id_array = []
for obj in jfile:
    fields = obj['fields']
    if len(Organization.objects.filter(name_eng=fields['name_eng'])) <= 0:
        prov = None
        if Province.objects.filter(pk=fields['province']):
            prov = Province.objects.get(pk=fields['province'])

        org = Organization(abbrev=fields['abbrev'], address=fields['address'], audio_file=fields['audio_file'],
                           city=fields['city'], council_quorum=fields['council_quorum'],
                           date_last_modified=fields['date_last_modified'],
                           dfo_contact_instructions=fields['dfo_contact_instructions'],
                           election_term=fields['election_term'], fax=fields['fax'],
                           fin=fields['fin'], former_name=fields['former_name'], key_species=fields['key_species'],
                           locked_by_ihub=fields['locked_by_ihub'], mailing_address=fields['mailing_address'],
                           name_eng=fields['name_eng'], name_ind=fields['name_ind'],
                           nation=fields['nation'], new_coucil_effective_date=fields['new_coucil_effective_date'],
                           notes=fields['notes'], old_id=fields['old_id'], phone=fields['phone'],
                           population_off_reserve=fields['population_off_reserve'],
                           population_on_reserve=fields['population_on_reserve'],
                           population_other_reserve=fields['population_other_reserve'],
                           postal_code=fields['postal_code'], province=prov,
                           relationship_rating=fields['relationship_rating'], website=fields['website'],
                           next_election=fields['next_election'], last_modified_by=me)
        org.save()

        org.grouping.set(fields['grouping'])
        org.orgs.set(fields['orgs'])
        org.regions.set(fields['regions'])
        org.reserves.set(fields['reserves'])
        org.sectors.set(fields['sectors'])

        org.processing_plant = fields['processing_plant'] if fields['processing_plant'] else 0
        org.wharf = fields['wharf'] if fields['wharf'] else 0

        org.save()

        id_array.append(org.pk)
    else:
        org = Organization.objects.get(name_eng=fields['name_eng'])
        id_array.append(org.pk)
        print("{} already exists".format(fields['name_eng']))


""" a simple function to export the important lookup tables. These fixtures will be used for testing and also for
seeding new instances"""
if not output_path:
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')

if not os.path.isdir(output_path):
    os.mkdir(output_path)

data = serializers.serialize("json", Organization.objects.filter(pk__in=id_array))
parsed = json.loads(data)
my_label = Organization._meta.db_table
f = open(os.path.join(output_path, f'{my_label}.json'), 'w', encoding='utf-8')
f.write(json.dumps(parsed, indent=4, sort_keys=True))
f.close()
