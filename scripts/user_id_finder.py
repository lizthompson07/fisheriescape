import csv

from django.contrib.auth import models


in_file = r'C:\Users\upsonp\Downloads\a_short_Users_list_sorted.txt'
out_file = r'C:\Users\upsonp\Downloads\out_put_user_id.txt'

names = []

file = csv.reader(open(in_file, 'r'), delimiter=" ")

with open(out_file, 'w', newline='\n') as outcsv:
    out_file = csv.writer(outcsv, delimiter=' ')
    for line in file:
        lastname = line[2]
        firstname = line[1]

        try:
            usr = models.User.objects.get(first_name=firstname, last_name=lastname, email__endswith="dfo-mpo.gc.ca")
            name = usr.last_name + ", " + usr.first_name
            if name not in names:
                out_file.writerow([usr.pk, name])
                names.append(name)
                print("{}: {}, {} - {}".format(usr.pk, usr.last_name, usr.first_name, usr.email))
        except models.User.DoesNotExist:
            name = lastname + ", " + firstname
            if name not in names:
                out_file.writerow(["-1", name])
                names.append(name)
                print("No match for '{}, {}'".format(lastname, firstname))
