# import xlsxwriter as xlsxwriter
# from django.template.defaultfilters import yesno
# from django.utils import timezone
# from django.conf import settings
# from django.utils.translation import gettext as _
#
# from lib.functions.custom_functions import listrify
# from lib.templatetags.verbose_names import get_verbose_label
# from . import models
# import os
#
#
# def generate_custom_list(provinces, groupings, sectors, regions, is_indigenous, species):
#     # figure out the filename
#     target_dir = os.path.join(settings.BASE_DIR, 'media', 'spot', 'temp')
#     target_file = "temp_export_{}.xlsx".format(timezone.now().strftime("%Y-%m-%d"))
#     target_file_path = os.path.join(target_dir, target_file)
#     target_url = os.path.join(settings.MEDIA_ROOT, 'spot', 'temp', target_file)
#
#     # create workbook and worksheets
#     workbook = xlsxwriter.Workbook(target_file_path)
#
#     # create formatting
#     header_format = workbook.add_format(
#         {'bold': True, 'border': 1, 'border_color': 'black', 'bg_color': '#D6D1C0', "align": 'normal', "text_wrap": True})
#     total_format = workbook.add_format({'bold': True, "align": 'left', "text_wrap": True, 'num_format': '$#,##0'})
#     normal_format = workbook.add_format({"align": 'left', "text_wrap": True, 'num_format': '$#,##0'})
#
#     # first, we need to develop a member_list
#     # starting with the entire list
#     member_list = models.OrganizationMember.objects.all()
#
#     if provinces != "None":
#         province_list = [models.Province.objects.get(pk=int(obj)) for obj in provinces.split(",")]
#         member_list = [member for member in member_list if member.organization.province in province_list]
#
#     if groupings != "None":
#         grouping_list = [models.Grouping.objects.get(pk=int(obj)) for obj in groupings.split(",")]
#         member_list = [member for group in grouping_list for member in member_list if group in member.organization.grouping.all()]
#
#     if sectors != "None":
#         sector_list = [models.Sector.objects.get(pk=int(obj)) for obj in sectors.split(",")]
#         member_list = [member for sector in sector_list for member in member_list if sector in member.organization.sectors.all()]
#
#     if regions != "None":
#         region_list = [models.Region.objects.get(pk=int(obj)) for obj in regions.split(",")]
#         member_list = [member for region in region_list for member in member_list if region in member.organization.regions.all()]
#
#     if is_indigenous == 1:
#         member_list = [member for member in member_list for grouping in member.organization.grouping.all() if grouping.is_indigenous]
#
#     if species != "None":
#         member_list = [member for member in member_list if str(member.organization.key_species).lower().find(species.lower()) >= 0]
#
#     # define the header
#     header = [
#         _("Group"),
#         _("Designation"),
#         _("First Name"),
#         _("Last Name"),
#         _("Role in Organization"),
#         _("Organization/Affiliation"),
#         _("Phone 1"),
#         _("Phone 2"),
#         _("Fax"),
#         _("Email 1"),
#         _("Email 2"),
#         _("Language Preference"),
#         _("Address"),
#         _("City"),
#         _("Province"),
#         _("Postal Code"),
#         _("Notes"),
#         _("DFO Contact Instructions / Liaison"),
#         _("DFO Sector"),
#         _("Region"),
#         _("Key Species"),
#     ]
#
#     # worksheets #
#     ##############
#     my_ws = workbook.add_worksheet(name="custom list")
#     col_max = [len(str(d)) if len(str(d)) <= 100 else 100 for d in header]
#     my_ws.write_row(0, 0, header, header_format)
#
#     i = 1
#     for member in member_list:
#         data_row = [
#             listrify(member.organization.grouping.all()),
#             member.person.designation,
#             member.person.first_name,
#             member.person.last_name,
#             str(member.organization),
#             member.role,
#             member.person.phone_1,
#             member.person.phone_2,
#             member.person.fax,
#             member.person.email_1,
#             member.person.email_2,
#             member.person.get_language_display(),
#             member.organization.address,
#             member.organization.city,
#             str(member.organization.province),
#             member.organization.postal_code,
#             member.organization.notes,
#             member.organization.dfo_contact_instructions,
#             listrify(member.organization.sectors.all()),
#             listrify(member.organization.regions.all()),
#             member.organization.key_species,
#         ]
#
#         # adjust the width of the columns based on the max string length in each col
#         ## replace col_max[j] if str length j is bigger than stored value
#
#         j = 0
#         for d in data_row:
#             # if new value > stored value... replace stored value
#             if len(str(d)) > col_max[j]:
#                 if len(str(d)) < 100:
#                     col_max[j] = len(str(d))
#                 else:
#                     col_max[j] = 100
#             j += 1
#
#         my_ws.write_row(i, 0, data_row, normal_format)
#         i += 1
#
#     # set column widths
#     for j in range(0, len(col_max)):
#         my_ws.set_column(j, j, width=col_max[j] * 1.1)
#
#     workbook.close()
#     return target_url
