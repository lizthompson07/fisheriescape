import xlrd
import os
import sys

# from csas.models import PubPublication
# from csas.models import ConContact

# Excel file name
file_name = '2021-2022_MAR_report_my_version_1.xls'

# The data file is expected to be in the [app]/scripts/data folder
file_path = os.path.dirname(os.path.realpath(__file__)) + os.path.sep + "data" + os.path.sep + file_name

# read in data
xls_data = xlrd.open_workbook(file_path)
sheet = xls_data.sheet_by_index(0)

num_rows = sheet.nrows
num_cols = sheet.ncols

print(' -- The number of rows: ', num_rows)
print(' -- The number of cols: ', num_cols)

# print(sheet.cell_value(1, 4))
# print(sheet.cell_value(0, 6), sheet.cell_value(46, 6))
# print(sheet.cell_value(0, 7), sheet.cell_value(46, 7))
# print(sheet.cell_value(0, 8), sheet.cell_value(46, 8))
# print(sheet.cell_value(0, 9), sheet.cell_value(46, 9))
# print(sheet.cell_value(0, 10), sheet.cell_value(46, 10))

for i in range(num_rows):
    if sheet.cell_value(i, 9) != "":
        print(sheet.cell_value(i, 9))

# find the column index for client_name
col_index = -1

for j in range(num_cols):
    # if sheet.cell_value(0, j) == "client_name":
    # if sheet.cell_value(0, j) == "ManagerName":
    # if sheet.cell_value(0, j) == "NameOfDirector":
    # if sheet.cell_value(0, j) == "NameOfCoordinator":
    # if sheet.cell_value(0, j) == "client_email":
    # if sheet.cell_value(0, j) == "client_sector":
    # if sheet.cell_value(0, j) == "region":
    # if sheet.cell_value(0, j) == "DirectorateBranch":
    # if sheet.cell_value(0, j) == "RequestType":
    # if sheet.cell_value(0, j) == "ApprovalDate":
    if sheet.cell_value(0, j) == "SubmissionDate":
        col_index = j

if col_index == -1:
    sys.exit(" -- Could not find client name in the sheet!")

# build a lead author list
client_list = []

for i in range(num_rows):
    client_name = sheet.cell_value(i, col_index)
    # remove all the spaces
    # client_name = client_name.replace(" ", "")
    # remove leading and ending spaces
    # client_name = client_name.strip()
    client_name = " ".join(client_name.split())

    # replace ',' with '/'
    # client_name = client_name.replace(",", "/")
    if client_name != "":
        client = [client_name]
        client_list.extend(client)
        # print(i, client_name)

# sort the client list
client_list.sort()

# remove the duplicates in the client list
client_list = list(dict.fromkeys(client_list))

for i in range(len(client_list)):
    print(i, client_list[i])

# write out the client name list to a text file
# file_name = 'request_client_list.txt'
# file_name = 'request_manager_list.txt'
# file_name = 'request_director_list.txt'
# file_name = 'request_coordinator_list.txt'
# file_name = 'request_client_sector_list.txt'
# file_name = 'request_region_list.txt'
# file_name = 'request_branch_list.txt'
# file_name = 'request_request_type_list.txt'
# file_name = 'request_approval_date_list.txt'
file_name = 'request_submission_date_list.txt'
file_path = os.path.dirname(os.path.realpath(__file__)) + os.path.sep + "data" + os.path.sep + file_name

f = open(file_path, "w")

# for i in range(len(client_list)):
for i in range(len(client_list)):
    # f.write("%5d, , " % (i+1))
    f.write("%5d, " % (i + 1))
    f.write(client_list[i])
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
