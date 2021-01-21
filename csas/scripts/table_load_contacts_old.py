import csv
import os

from csas.models import ConContact

# data file name
# file_name = 'contacts.csv'
file_name = 'Publications_Contacts.csv'
# The data file is expected to be in the [app]/scripts/data folder
file_path = os.path.dirname(os.path.realpath(__file__)) + os.path.sep + "data" + os.path.sep + file_name

csv_file = open(file_path)
csv_data = csv.reader(csv_file, delimiter=',')

print(' -- Inserting data into CSAS table CONCONTACT ............')
for row in csv_data:

    # remove all the spaces in the list
    row = [elem.strip(' ') for elem in row]

    print("{}, {}".format(row[3], row[2]))
    if not ConContact.objects.filter(last_name=row[3], first_name=row[2]):
        ConContact(honorific_id=row[1],
                   first_name=row[2],
                   last_name=row[3],
                   affiliation=row[4],
                   region_id=row[5],
                   sector_id=row[6],
                   role_id = row[7],
                   job_title=row[8],
                   language_id=row[9],
                   contact_type_id=row[10],
                   status_id=row[11],
                   notification_preference_id=row[12],
                   phone=row[13],
                   email=row[14],
                   expertise_id=row[15],
                   cc_grad_id=row[16],
                   notes=row[17]
                   ).save()
    else:
        print("Found")

# close the connection to the database.
print(" -- Done")
