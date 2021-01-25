import xlrd
import os
import sys
import unicodedata

# from csas.models import PubPublication
# from csas.models import ConContact

# Excel file name
file_name = '2021-2022_MAR_report_my_version_2.xls'

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
    if sheet.cell_value(0, j) == "file":
        col_index_file = j
    elif sheet.cell_value(0, j) == "assigned_id":
        col_index_assigned_id = j
    elif sheet.cell_value(0, j) == "title":
        col_index_title = j
    elif sheet.cell_value(0, j) == "client_name":
        col_index_client_name = j
    elif sheet.cell_value(0, j) == "client_title":
        col_index_client_title = j
    elif sheet.cell_value(0, j) == "client_email":
        col_index_client_email = j
    elif sheet.cell_value(0, j) == "client_sector":
        col_index_client_sector = j
    elif sheet.cell_value(0, j) == "ManagerName":
        col_index_ManagerName = j
    elif sheet.cell_value(0, j) == "region":
        col_index_region = j
    elif sheet.cell_value(0, j) == "DirectorateBranch":
        col_index_DirectorateBranch = j
    elif sheet.cell_value(0, j) == "Zonal":
        col_index_Zonal = j
    elif sheet.cell_value(0, j) == "ZonalText":
        col_index_ZonalText = j
    elif sheet.cell_value(0, j) == "issue":
        col_index_issue = j
    elif sheet.cell_value(0, j) == "RequestType":
        col_index_RequestType = j
    elif sheet.cell_value(0, j) == "Assistance":
        col_index_Assistance = j
    elif sheet.cell_value(0, j) == "AssistanceText":
        col_index_AssistanceText = j
    elif sheet.cell_value(0, j) == "RationaleForContextText":
        col_index_RationaleForContextText = j
    elif sheet.cell_value(0, j) == "ConsequenceText":
        col_index_ConsequenceText = j
    elif sheet.cell_value(0, j) == "FiscalYearText":
        col_index_FiscalYearText = j
    elif sheet.cell_value(0, j) == "rationale_for_timing":
        col_index_rationale_for_timing = j
    elif sheet.cell_value(0, j) == "proposed_timing":
        col_index_proposed_timing = j
    elif sheet.cell_value(0, j) == "funding":
        col_index_funding = j
    elif sheet.cell_value(0, j) == "FundsText":
        col_index_FundsText = j
    elif sheet.cell_value(0, j) == "NameOfDirector":
        col_index_NameOfDirector = j
    elif sheet.cell_value(0, j) == "NameOfCoordinator":
        col_index_NameOfCoordinator = j
    elif sheet.cell_value(0, j) == "ApprovalDate":
        col_index_ApprovalDate = j
    elif sheet.cell_value(0, j) == "SubmissionDate":
        col_index_SubmissionDate = j
    elif sheet.cell_value(0, j) == "ReceivedDate":
        col_index_ReceivedDate = j

# if col_index == -1:
#     sys.exit(" -- Could not find client name in the sheet!")

# print(' -- the index = ', col_index)
# build a lead author list
# client_list = []

# for i in range(num_rows):
#     client_name = sheet.cell_value(i, col_index)
#     # remove all the spaces
#     # client_name = client_name.replace(" ", "")
#     # remove leading and ending spaces
#     # client_name = client_name.strip()
#     client_name = " ".join(client_name.split())

#     # replace ',' with '/'
#     # client_name = client_name.replace(",", "/")
#     if client_name != "":
#         client = [client_name]
#         client_list.extend(client)
#        # print(i, client_name)

# sort the client list
# client_list.sort()

# remove the duplicates in the client list
# client_list = list(dict.fromkeys(client_list))

# for i in range(len(client_list)):
#     print(i, client_list[i])

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
file_name = 'request_submission.json'
file_path = os.path.dirname(os.path.realpath(__file__)) + os.path.sep + "data" + os.path.sep + file_name

f = open(file_path, "w")

lef = '{'
rit = '}'
sp4 = ' '*4
sp8 = ' '*8
sp12 = ' '*12

f.write("[\n")
# for i in range(len(client_list)):
# for i in range(num_rows - 1):
num_of_rows = 24
for i in range(num_of_rows):
    pk = i + 1
    f.write('{sp4}{lef}\n'.format(sp4=sp4, lef=lef))
    f.write('{sp8}\"model\": \"csas.reqrequest\",\n'.format(sp8=sp8))
    f.write('{sp8}\"pk\": {pk},\n'.format(sp8=sp8, pk=pk))
    f.write('{sp8}\"fields\": {lef}\n'.format(sp8=sp8, lef=lef))

    f.write('{sp12}\"assigned_req_id\": null,\n'.format(sp12=sp12))
    f.write('{sp12}\"in_year_request\": null,\n'.format(sp12=sp12))

    title = sheet.cell_value(pk, col_index_title)
    f.write('{sp12}\"title\": \"{title}\",\n'.format(sp12=sp12, title=title))

    file = sheet.cell_value(pk, col_index_file)
    f.write('{sp12}\"file\": \"{file}\",\n'.format(sp12=sp12, file=file))

    region = sheet.cell_value(pk, col_index_region)
    f.write('{sp12}\"region\": {region},\n'.format(sp12=sp12, region=region))

    branch = sheet.cell_value(pk, col_index_DirectorateBranch)
    # branch = 'null'
    f.write('{sp12}\"directorate_branch\": {branch},\n'.format(sp12=sp12, branch=branch))

    sector = sheet.cell_value(pk, col_index_client_sector)
    # sector = 2
    f.write('{sp12}\"client_sector\": {sector},\n'.format(sp12=sp12, sector=sector))

    client_title = sheet.cell_value(pk, col_index_client_title)
    f.write('{sp12}\"client_title\": \"{client_title}\",\n'.format(sp12=sp12, client_title=client_title))

    email = sheet.cell_value(pk, col_index_client_email)
    f.write('{sp12}\"client_email\": \"{email}\",\n'.format(sp12=sp12, email=email))

    request_type = sheet.cell_value(pk, col_index_RequestType)
    request_type = 'null'
    f.write('{sp12}\"request_type\": {request_type},\n'.format(sp12=sp12, request_type=request_type))

    zonal = sheet.cell_value(pk, col_index_Zonal)
    zonal = 'null'
    f.write('{sp12}\"zonal\": {zonal},\n'.format(sp12=sp12, zonal=zonal))

    zonal_text = sheet.cell_value(pk, col_index_ZonalText)
    zonal_text = zonal_text.replace("\n", "\\n")
    # zonal_text = "aaa"
    f.write('{sp12}\"zonal_text\": \"{zonal_text}\",\n'.format(sp12=sp12, zonal_text=zonal_text))

    issue = sheet.cell_value(pk, col_index_issue)
    issue = issue.replace("\n", "\\n")
    f.write('{sp12}\"issue\": \"{issue}\",\n'.format(sp12=sp12, issue=issue))

    conseq_text = sheet.cell_value(pk, col_index_ConsequenceText)
    conseq_text = conseq_text.replace("\n", "\\n")
    # conseq_text = "bbb"
    f.write('{sp12}\"consequence_text\": \"{conseq_text}\",\n'.format(sp12=sp12, conseq_text=conseq_text))

    assistance = sheet.cell_value(pk, col_index_Assistance)
    assistance = 'null'
    f.write('{sp12}\"assistance\": {assistance},\n'.format(sp12=sp12, assistance=assistance))

    assistance_text = sheet.cell_value(pk, col_index_AssistanceText)
    assistance_text = assistance_text.replace("\n", "\\n")
    # assistance_text = "ccc"
    f.write('{sp12}\"assistance_text\": \"{assistance_text}\",\n'.format(sp12=sp12, assistance_text=assistance_text))

    priority = 'high'
    priority = 1
    f.write('{sp12}\"priority\": {priority},\n'.format(sp12=sp12, priority=priority))

    rationale = sheet.cell_value(pk, col_index_RationaleForContextText)
    rationale = rationale.replace("\n", "\\n")
    rationale = rationale.replace("'", "\'")
    f.write('{sp12}\"rationale\": \"{rationale}\",\n'.format(sp12=sp12, rationale=rationale))

    proposed_timing = sheet.cell_value(pk, col_index_proposed_timing)
    proposed_timing = 1
    f.write('{sp12}\"proposed_timing\": {proposed_timing},\n'.format(sp12=sp12, proposed_timing=proposed_timing))

    rationale_4_timing = sheet.cell_value(pk, col_index_rationale_for_timing)
    rationale_4_timing = rationale_4_timing.replace("\n", "\\n")
    # rationale_4_timing = "ddd"
    f.write('{sp12}\"rationale_for_timing\": \"{rationale_4_timing}\",\n'.format(sp12=sp12, rationale_4_timing=rationale_4_timing))

    funding = sheet.cell_value(pk, col_index_funding)
    funding = 'false'
    f.write('{sp12}\"funding\": {funding},\n'.format(sp12=sp12, funding=funding))

    funding_notes = sheet.cell_value(pk, col_index_FundsText)
    funding_notes = funding_notes.replace("\n", "\\n")
    # funding_notes = "eee"
    f.write('{sp12}\"funding_notes\": \"{funding_notes}\",\n'.format(sp12=sp12, funding_notes=funding_notes))

    science_discussion = 'false'
    f.write('{sp12}\"science_discussion\": {science_discussion},\n'.format(sp12=sp12, science_discussion=science_discussion))

    sci_dis_notes = 'NA'
    f.write('{sp12}\"science_discussion_notes\": \"{sci_dis_notes}\",\n'.format(sp12=sp12, sci_dis_notes=sci_dis_notes))

    fiscal_year = sheet.cell_value(pk, col_index_FiscalYearText)
    f.write('{sp12}\"fiscal_year_text\": \"{fiscal_year}\",\n'.format(sp12=sp12, fiscal_year=fiscal_year))

    adviser_sub = 'null'
    f.write('{sp12}\"adviser_submission\": {adviser_sub},\n'.format(sp12=sp12, adviser_sub=adviser_sub))

    rd_sub = 'null'
    f.write('{sp12}\"rd_submission\": {rd_sub},\n'.format(sp12=sp12, rd_sub=rd_sub))

    decision_date = 'null'
    f.write('{sp12}\"decision_date\": {decision_date},\n'.format(sp12=sp12, decision_date=decision_date))

    client_name = sheet.cell_value(pk, col_index_client_name)
    # client_name = 5
    f.write('{sp12}\"client_name\": [{client_name}],\n'.format(sp12=sp12, client_name=client_name))

    manager_name = sheet.cell_value(pk, col_index_ManagerName)
    # manager_name = 2
    f.write('{sp12}\"manager_name\": [{manager_name}],\n'.format(sp12=sp12, manager_name=manager_name))

    coor_name = sheet.cell_value(pk, col_index_NameOfCoordinator)
    f.write('{sp12}\"coordinator_name\": [{coor_name}],\n'.format(sp12=sp12, coor_name=coor_name))

    dir_name = sheet.cell_value(pk, col_index_NameOfDirector)
    f.write('{sp12}\"director_name\": [{dir_name}]\n'.format(sp12=sp12, dir_name=dir_name))

    f.write('{sp8}{rit}\n'.format(sp8=sp8, rit=rit))

    f.write('{sp4}{rit}'.format(sp4=sp4, rit=rit))

    if pk < num_of_rows:
        f.write(",\n")
    else:
        f.write("\n")

f.write("]\n")
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
