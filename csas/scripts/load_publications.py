import xlrd
import os
import sys

from csas.models import PubPublication
from csas.models import ConContact

# Excel file name
file_name = 'Publications.xls'

# The data file is expected to be in the [app]/scripts/data folder
file_path = os.path.dirname(os.path.realpath(__file__)) + os.path.sep + "data" + os.path.sep + file_name

# read in data
xls_data = xlrd.open_workbook(file_path)
sheet = xls_data.sheet_by_index(0)

num_rows = sheet.nrows
num_cols = sheet.ncols

print(' -- The number of rows: ', num_rows)
print(' -- The number of cols: ', num_cols)

print(sheet.cell_value(1, 4))
print(sheet.cell_value(0, 6), sheet.cell_value(8783, 6))
print(sheet.cell_value(0, 7), sheet.cell_value(8783, 7))
print(sheet.cell_value(0, 8), sheet.cell_value(8783, 8))
print(sheet.cell_value(0, 9), sheet.cell_value(8783, 9))
print(sheet.cell_value(0, 10), sheet.cell_value(8783, 10))

for i in range(num_rows):
    if sheet.cell_value(i, 9) != "":
        print(sheet.cell_value(i, 9))

# find the column index for lead_author
col_index = -1

for j in range(num_cols):
    if sheet.cell_value(0, j) == "lead_author":
        col_index = j

if col_index == -1:
    sys.exit(" -- Could not find lead author in the sheet!")

# build a lead author list
author_list = []

for i in range(num_rows):
    lead_author = sheet.cell_value(i, col_index)
    # remove all the spaces
    # lead_author = lead_author.replace(" ", "")
    # remove leading and ending spaces
    # lead_author = lead_author.strip()
    lead_author = " ".join(lead_author.split())

    # replace ',' with '/'
    # lead_author = lead_author.replace(",", "/")
    if lead_author != "":
        author = [lead_author]
        author_list.extend(author)
        # print(i, lead_author)

# sort the author list
author_list.sort()

# remove the duplicates in the author list
author_list = list(dict.fromkeys(author_list))

for i in range(len(author_list)):
    print(i, author_list[i])

# write out the lead author list to a text file
file_name = 'Publications.txt'
file_path = os.path.dirname(os.path.realpath(__file__)) + os.path.sep + "data" + os.path.sep + file_name

f = open(file_path, "w")

# for i in range(len(author_list)):
for i in range(4500):
    # f.write("%5d, , " % (i+1))
    f.write("%5d, " % (i + 1))
    f.write(author_list[i])
    # f.write(" ,  ,  ,  ,  ,  ,  , 1,  ,  , 1, 1,  ,  ,  ,  ")
    f.write("\n")

# f.writelines(author_list)
f.close()


#for row in csv_data:

    # remove all the spaces in the list
    # row = [elem.strip(' ') for elem in row]

    # I'm going to assume the title for a request is suppose to be unique
#    if not PubPublication.objects.filter(title_en=row[1]):
#        print("Inserting publication {}".format(row[1]))
        # PubPublication(title_en=row[1],
        #                title_fr=row[2],
        #                title_in=row[3],
        #                pub_year=row[4],
        #                pub_num=row[5],
        #                pages=row[6],
        #                pdf_size=row[7],
        #                keywords=row[8],
        #                citation=row[9],
        #                description=row[10],
        #                lead_author_id=row[11],
        #                other_author_id=row[12],
        #                client_id=row[13],
        #                series_id=row[14],
        #                lead_region_id=row[15]
        #                ).save()


# close the connection to the database.
print(" -- Done")
