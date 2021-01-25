# import html2text as html2text
# import xlsxwriter as xlsxwriter
# from django.conf import settings
# from django.db.models import Q
# from django.template.defaultfilters import yesno
#
# from shared_models import models as shared_models
# from lib.functions.custom_functions import nz
# from lib.functions.verbose_field_name import verbose_field_name
# from . import models
# import os
#
#
# def generate_master_spreadsheet(fy, rc, project):
#     # figure out the filename
#     target_dir = os.path.join(settings.BASE_DIR, 'media', 'scifi', 'temp')
#     target_file = "temp_export.xlsx"
#     target_file_path = os.path.join(target_dir, target_file)
#     target_url = os.path.join(settings.MEDIA_ROOT, 'scifi', 'temp', target_file)
#
#     # create workbook and worksheets
#     workbook = xlsxwriter.Workbook(target_file_path)
#     worksheet1 = workbook.add_worksheet(name="Transactions")
#
#     # create formatting
#     header_format = workbook.add_format(
#         {'bold': True, 'border': 1, 'border_color': 'black', 'bg_color': '#8C96A0', "align": 'normal',
#          "text_wrap": True})
#     total_format = workbook.add_format({'bg_color': '#D6D1C0', "align": 'left', "text_wrap": True})
#     normal_format = workbook.add_format({"align": 'left', "text_wrap": True})
#     bold_format = workbook.add_format({"align": 'left', 'bold': True})
#
#     # need to assemble a transaction list
#     transaction_list = models.Transaction.objects.filter(fiscal_year=fy)
#     if rc != "None":
#         transaction_list = transaction_list.filter(responsibility_center_id=int(rc))
#     if project != "None":
#         transaction_list = transaction_list.filter(project_id=int(project))
#
#     # spreadsheet: Project List #
#     #############################
#     if len(transaction_list) == 0:
#         worksheet1.write_row(0, 0, ["There are no transactions to report", ], bold_format)
#     else:
#         # get a project list for the year
#         field_list = [
#             'fiscal_year',
#             'responsibility_center',
#             'business_line',
#             'allotment_code',
#             'line_object',
#             'project',
#             'transaction_type',
#             'supplier_description',
#             'expected_purchase_date',
#             'creation_date',
#             'obligation_cost',
#             'outstanding_obligation',
#             'invoice_cost',
#             'reference_number',
#             'invoice_date',
#             'in_mrs',
#             'amount_paid_in_mrs',
#             'mrs_notes',
#             'procurement_hub_contact',
#             'comment',
#             'created_by',
#             'exclude_from_rollup',
#         ]
#         header = ["ID", ]
#         header.extend([verbose_field_name(transaction_list[0], field) for field in field_list])
#
#         # create the col_max column to store the length of each header
#         # should be a maximum column width to 100
#         col_max = [len(str(d)) if len(str(d)) <= 100 else 100 for d in header]
#
#         worksheet1.write_row(0, 0, header, header_format)
#
#         i = 1
#         for t in transaction_list:
#
#             if t.expected_purchase_date:
#                 expected_purchase_date = t.expected_purchase_date.strftime("%Y-%m-%d")
#             else:
#                 expected_purchase_date = t.expected_purchase_date
#
#             if t.creation_date:
#                 creation_date = t.creation_date.strftime("%Y-%m-%d")
#             else:
#                 creation_date = t.creation_date
#
#             if t.invoice_date:
#                 invoice_date = t.invoice_date.strftime("%Y-%m-%d")
#             else:
#                 invoice_date = t.invoice_date
#
#             data_row = [
#                 t.id,
#                 str(t.fiscal_year),
#                 str(t.responsibility_center),
#                 str(t.business_line),
#                 str(t.allotment_code),
#                 str(t.line_object),
#                 str(t.project),
#                 t.get_transaction_type_display(),
#                 t.supplier_description,
#                 expected_purchase_date,
#                 creation_date,
#                 t.obligation_cost,
#                 t.outstanding_obligation,
#                 t.invoice_cost,
#                 t.reference_number,
#                 invoice_date,
#                 t.in_mrs,
#                 t.amount_paid_in_mrs,
#                 t.mrs_notes,
#                 t.procurement_hub_contact,
#                 t.comment,
#                 str(t.created_by),
#                 t.exclude_from_rollup,
#             ]
#
#
#             # adjust the width of the columns based on the max string length in each col
#             ## replace col_max[j] if str length j is bigger than stored value
#
#             j = 0
#             for d in data_row:
#                 # if new value > stored value... replace stored value
#                 if len(str(d)) > col_max[j]:
#                     if len(str(d)) < 100:
#                         col_max[j] = len(str(d))
#                     else:
#                         col_max[j] = 100
#                 j += 1
#
#             worksheet1.write_row(i, 0, data_row, normal_format)
#             i += 1
#
#         for j in range(0, len(col_max)):
#             worksheet1.set_column(j, j, width=col_max[j] * 1.1)
#
#     workbook.close()
#     return target_url
