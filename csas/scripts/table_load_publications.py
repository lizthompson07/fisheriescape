import csv
import os

from csas.models import PubPublication

# data file name
file_name = 'publications.csv'
# The data file is expected to be in the [app]/scripts/data folder
file_path = os.path.dirname(os.path.realpath(__file__)) + os.path.sep + "data" + os.path.sep + file_name

csv_file = open(file_path)
csv_data = csv.reader(csv_file, delimiter=',')

print(' -- Inserting data into CSAS table PUBLICATION ............')
for row in csv_data:

    # remove all the spaces in the list
    row = [elem.strip(' ') for elem in row]

    # I'm going to assume the title for a request is suppose to be unique
    if not PubPublication.objects.filter(title_en=row[1]):
        print("Inserting publication {}".format(row[1]))
        PubPublication(title_en=row[1],
                       title_fr=row[2],
                       title_in=row[3],
                       pub_year=row[4],
                       pub_num=row[5],
                       pages=row[6],
                       pdf_size=row[7],
                       keywords=row[8],
                       citation=row[9],
                       description=row[10],
                       lead_author_id=row[11],
                       other_author_id=row[12],
                       client_id=row[13],
                       series_id=row[14],
                       lead_region_id=row[15]
                       ).save()


# close the connection to the database.
print(" -- Done")
