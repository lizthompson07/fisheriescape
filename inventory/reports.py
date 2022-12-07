import os
import shutil

import xlsxwriter as xlsxwriter
from django.conf import settings
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from html2text import html2text

from lib.functions.custom_functions import listrify
from lib.templatetags.custom_filters import nz
from lib.templatetags.verbose_names import get_verbose_label, get_field_value
from shared_models import models as shared_models
from . import models
from . import xml_export


def generate_batch_xml(sections):
    # figure out the filenames etc..
    #################################
    # this will be the target dir of the zipfile
    zip_dir = os.path.join(settings.BASE_DIR, 'media', 'inventory', 'temp')
    # this is the filename for the zip file (the zipping function will include the .zip extention)
    zip_filename = "temp_export_{}".format(timezone.now().strftime("%Y-%m-%d"))
    # this is the full path to the target zip file
    zip_file_path = os.path.join(zip_dir, zip_filename)
    # this is the url to the target zip file.. is what is returned by the function
    target_url = os.path.join(settings.MEDIA_ROOT, 'inventory', 'temp', "{}.zip".format(zip_filename))
    # this will be the target dir of the xml files
    xml_dir = os.path.join(settings.BASE_DIR, 'media', 'inventory', 'temp', 'zipdir')

    # clean out the zip_dir directory and subdir
    for root, dirs, files in os.walk(zip_dir):
        for file in files:
            os.remove(os.path.join(root, file))

    # start with all resources
    resource_list = models.Resource.objects.all()
    # parse out the sections arg and refine the list
    if sections != "None":
        section_list = [shared_models.Section.objects.get(pk=int(obj)) for obj in sections.split(",")]
        resource_list = [resource for resource in resource_list if resource.section in section_list]

    # generate an xml file for each resource in resource_list
    for resource in resource_list:
        # get the xml data
        xml_data = xml_export.construct(resource, pretty=False)
        # figure out the filename
        xml_filename = "xml_metadata_export_{}.xml".format(resource.id)
        target_file_path = os.path.join(xml_dir, xml_filename)
        # write xml data to file
        xml_data.write(target_file_path)

    # zip the folder
    # adapted from https://stackoverflow.com/questions/1855095/how-to-create-a-zip-archive-of-a-directory
    shutil.make_archive(zip_file_path, 'zip', xml_dir)

    return target_url


def generate_odi_report():
    # figure out the filename
    target_dir = os.path.join(settings.BASE_DIR, 'media', 'inventory', 'temp')
    target_file = "temp_data_export_{}.xlsx".format(timezone.now().strftime("%Y-%m-%d"))
    target_file_path = os.path.join(target_dir, target_file)
    target_url = os.path.join(settings.MEDIA_ROOT, 'inventory', 'temp', target_file)
    # create workbook and worksheets
    workbook = xlsxwriter.Workbook(target_file_path)
    # create formatting variables
    title_format = workbook.add_format(
        {'bold': False, "align": 'normal', 'font_size': 14, "text_wrap": False, 'bg_color': '#006640', 'font_color': 'white'})
    header_format = workbook.add_format(
        {'bold': False, 'border': 1, 'border_color': 'black', 'bg_color': '#A1B7BF', "align": 'normal', "text_wrap": False})

    normal_format = workbook.add_format({"align": 'left', "text_wrap": True, })
    date_format = workbook.add_format({'num_format': "yyyy-mm-dd", "align": 'left', })

    # get the trip list
    resource_list = models.Resource.objects.filter(odi_id__isnull=False)

    field_list = [
        "odi_id",
        "title_eng",
        "title_fre",
        "descr_eng",
        "descr_fre",
        "publisher_en",
        "publisher_fr",
        "od_publication_date",
        "language",
        "size",
        "eligible_for_release",
        "paa_en",
        "paa_fr",
        "od_release_date",
        "url_en",
        "url_fr",
    ]

    # define the headers
    header1 = ["dfo-mpo",
               "Open Data Inventory        Fisheries and Oceans Canada | Pêches et Océans Canada",
               "",
               "",
               "",
               "",
               "",
               "",
               "",
               "",
               "",
               "",
               "",
               "",
               "",
               "",
               ]
    header2 = ["Reference Number",
               "Title (English)",
               "Title (French)",
               "Description (English)",
               "Description (French)",
               "Publisher - Name at Publication (English)",
               "Publisher - Name at Publication (French)",
               "Date Published",
               "Language",
               "Size",
               "Eligible for Release",
               "Program Alignment Architecture (English)",
               "Program Alignment Architecture (French)",
               "Date Released",
               "Open Government Portal Record (English)",
               "Open Government Portal Record (French)", ]
    header3 = ["ref_number",
               "title_en",
               "title_fr",
               "description_en",
               "description_fr",
               "publisher_en",
               "publisher_fr",
               "date_published",
               "language",
               "size",
               "eligible_for_release",
               "program_alignment_architecture_en",
               "program_alignment_architecture_fr",
               "date_released",
               "portal_url_en",
               "portal_url_fr",
               ]
    # header.append('Number of projects tagged')

    # define a worksheet
    my_ws = workbook.add_worksheet(name="trip list")
    my_ws.write_row(0, 0, header1, title_format)
    my_ws.write_row(1, 0, header2, header_format)
    my_ws.write_row(2, 0, header3, header_format)
    my_ws.set_row(2, 0)  # row # 2 is a hidden row

    i = 3
    for r in resource_list.order_by("odi_id"):
        # create the col_max column to store the length of each header
        # should be a maximum column width to 100
        col_max = [len(str(d)) if len(str(d)) <= 100 else 100 for d in header2]

        j = 0
        for field in field_list:

            if "publisher_en" in field:
                my_val = "Fisheries and Oceans"
                my_ws.write(i, j, my_val, normal_format)

            elif "publisher_fr" in field:
                my_val = "Pêches et Océans"
                my_ws.write(i, j, my_val, normal_format)

            elif "eligible_for_release" in field:
                my_val = "Y"
                my_ws.write(i, j, my_val, normal_format)

            elif "language" in field:
                my_val = "en+fr" if r.od_publication_date else ""
                my_ws.write(i, j, my_val, normal_format)

            elif "paa_en" in field:
                my_val = listrify([f'{paa.code} {paa.name}' for paa in r.paa_items.all()])
                my_ws.write(i, j, my_val, normal_format)

            elif "paa_fr" in field:
                my_val = listrify([f'{paa.code} {paa.nom}' for paa in r.paa_items.all()])
                my_ws.write(i, j, my_val, normal_format)

            elif "url_en" in field:
                if r.public_url:
                    my_val = f'https://open.canada.ca/data/en/dataset/{r.uuid}'
                else:
                    my_val = ""
                my_ws.write_url(i, j, url=my_val, string=my_val)
            elif "url_fr" in field:
                if r.public_url:
                    my_val = f'https://ouvert.canada.ca/data/fr/dataset/{r.uuid}'
                else:
                    my_val = ""
                my_ws.write_url(i, j, url=my_val, string=my_val)
            elif "date" in field:
                my_val = get_field_value(r, field, nullmark="")
                my_ws.write(i, j, my_val, date_format)
            else:
                my_val = get_field_value(r, field, nullmark="")
                my_ws.write(i, j, my_val, normal_format)

            # adjust the width of the columns based on the max string length in each col
            ## replace col_max[j] if str length j is bigger than stored value

            # if new value > stored value... replace stored value
            if len(str(my_val)) > col_max[j]:
                if len(str(my_val)) < 75:
                    col_max[j] = len(str(my_val))
                else:
                    col_max[j] = 75
            j += 1
        i += 1

        # set column widths
        for j in range(0, len(col_max)):
            my_ws.set_column(j, j, width=col_max[j] * 1.1)

    workbook.close()
    return target_url


def generate_physical_samples_report():
    # figure out the filename
    target_dir = os.path.join(settings.BASE_DIR, 'media', 'inventory', 'temp')
    target_file = "temp_data_export_{}.xlsx".format(timezone.now().strftime("%Y-%m-%d"))
    target_file_path = os.path.join(target_dir, target_file)
    target_url = os.path.join(settings.MEDIA_ROOT, 'inventory', 'temp', target_file)
    # create workbook and worksheets
    workbook = xlsxwriter.Workbook(target_file_path)
    # create formatting variables
    title_format = workbook.add_format(
        {'bold': False, "align": 'normal', 'font_size': 14, "text_wrap": False, 'bg_color': '#006640', 'font_color': 'white'})
    header_format = workbook.add_format(
        {'bold': False, 'border': 1, 'border_color': 'black', 'bg_color': '#A1B7BF', "align": 'normal', "text_wrap": False})

    normal_format = workbook.add_format({"align": 'left', "text_wrap": True, })
    date_format = workbook.add_format({'num_format': "yyyy-mm-dd", "align": 'left', })

    # get the resource list
    # anything with resource type as "physical collection"
    ids = [r.id for r in models.Resource.objects.filter(resource_type_id=4)]
    # anything where this is a meaningful description of physical samples
    ids.extend(
        [r.id for r in models.Resource.objects.filter(physical_sample_descr_eng__isnull=False) if len(r.physical_sample_descr_eng) > 10])
    ids.extend(
        [r.id for r in models.Resource.objects.filter(physical_sample_descr_fre__isnull=False) if len(r.physical_sample_descr_fre) > 10])
    # anything where the word "physical" is in the title
    ids.extend(
        [r.id for r in models.Resource.objects.filter(title_eng__icontains="physical").filter(title_eng__icontains="sample")])
    ids.extend(
        [r.id for r in models.Resource.objects.filter(title_fre__icontains="physique").filter(title_fre__icontains="échantillon")])
    # anything where the word "physical" is in the storage notes
    ids.extend(
        [r.id for r in models.Resource.objects.filter(storage_envr_notes__icontains="physical").filter(storage_envr_notes__icontains="sample")])
    ids.extend(
        [r.id for r in models.Resource.objects.filter(storage_envr_notes__icontains="physique").filter(storage_envr_notes__icontains="échantillon")])

    resources = models.Resource.objects.filter(id__in=ids)

    field_list = [
        "id",
        "title_eng",
        "title_fre",
        "physical_sample_descr_eng",
        "physical_sample_descr_fre",
        "storage_envr_notes",
        "hyperlink",
    ]

    # define the headers
    header0 = ["dfo-mpo",
               "Physical Samples Report        Fisheries and Oceans Canada | Pêches et Océans Canada",
               "",
               "",
               "",
               "",
               "",
               ]
    header = [get_verbose_label(resources.first(), field) for field in field_list]

    # header.append('Number of projects tagged')

    # define a worksheet
    my_ws = workbook.add_worksheet(name="query results")
    my_ws.write_row(0, 0, header0, title_format)
    my_ws.write_row(2, 0, header, header_format)

    i = 3
    for r in resources.order_by("id"):
        # create the col_max column to store the length of each header
        # should be a maximum column width to 100
        col_max = [len(str(d)) if len(str(d)) <= 100 else 100 for d in header]

        j = 0
        for field in field_list:
            if "hyperlink" in field:
                my_val = f'http://dmapps{reverse("inventory:resource_detail", args=[r.id])}'
                my_ws.write_url(i, j, url=my_val, string=my_val)
            else:
                my_val = get_field_value(r, field, nullmark="")
                my_ws.write(i, j, my_val, normal_format)

            # adjust the width of the columns based on the max string length in each col
            ## replace col_max[j] if str length j is bigger than stored value

            # if new value > stored value... replace stored value
            if len(str(my_val)) > col_max[j]:
                if len(str(my_val)) < 75:
                    col_max[j] = len(str(my_val))
                else:
                    col_max[j] = 75
            j += 1
        i += 1

        # set column widths
        for j in range(0, len(col_max)):
            my_ws.set_column(j, j, width=col_max[j] * 1.1)

    workbook.close()
    return target_url


def generate_resources_report(sections):
    # figure out the filename
    target_dir = os.path.join(settings.BASE_DIR, 'media', 'inventory', 'temp')
    target_file = "temp_data_export_{}.xlsx".format(timezone.now().strftime("%Y-%m-%d"))
    target_file_path = os.path.join(target_dir, target_file)
    target_url = os.path.join(settings.MEDIA_ROOT, 'inventory', 'temp', target_file)
    # create workbook and worksheets
    workbook = xlsxwriter.Workbook(target_file_path)
    # create formatting variables
    title_format = workbook.add_format(
        {'bold': False, "align": 'normal', 'font_size': 14, "text_wrap": False, 'bg_color': '#006640', 'font_color': 'white'})
    header_format = workbook.add_format(
        {'bold': False, 'border': 1, 'border_color': 'black', 'bg_color': '#A1B7BF', "align": 'normal', "text_wrap": False})

    normal_format = workbook.add_format({"align": 'left', "text_wrap": True, })
    date_format = workbook.add_format({'num_format': "yyyy-mm-dd", "align": 'left', })

    # get the resource list
    # anything with resource type as "physical collection"

    resources = models.Resource.objects.all()
    if sections and sections != "None":
        sections = sections.split(",")
        resources = resources.filter(section_id__in=sections)

    field_list = [
        "uuid",
        "resource_type",
        "section",
        "title_eng",
        "title_fre",
        "status",
        "maintenance",
        "purpose_eng",
        "purpose_fre",
        "descr_eng",
        "descr_fre",
        "time_start_day",
        "time_start_month",
        "time_start_year",
        "time_end_day",
        "time_end_month",
        "time_end_year",
        "sampling_method_eng",
        "sampling_method_fre",
        "physical_sample_descr_eng",
        "physical_sample_descr_fre",
        "resource_constraint_eng",
        "resource_constraint_fre",
        "qc_process_descr_eng",
        "qc_process_descr_fre",
        "security_use_limitation_eng",
        "security_use_limitation_fre",
        "security_classification",
        "storage_envr_notes",
        "distribution_formats",
        "data_char_set",
        "spat_representation",
        "spat_ref_system",
        "geo_descr_eng",
        "geo_descr_fre",
        "west_bounding",
        "south_bounding",
        "east_bounding",
        "north_bounding",
        "parameters_collected_eng",
        "parameters_collected_fre",
        "additional_credit",
        "analytic_software",
        "date_verified",
        "fgp_url",
        "public_url",
        "fgp_publication_date",
        "od_publication_date",
        "od_release_date",
        "odi_id",
        "last_revision_date",
        "open_data_notes",
        "notes",
        "citations2",
        "keywords",
        "people",
        "paa_items",
        "parent",
        "date_last_modified",
        "last_modified_by",
        "flagged_4_deletion",
        "flagged_4_publication",
        "completedness_report",
        "completedness_rating",
        "translation_needed",
        "publication_fy",

        "hyperlink",
    ]
    header = [get_verbose_label(resources.first(), field) for field in field_list]

    # header.append('Number of projects tagged')

    # define a worksheet
    my_ws = workbook.add_worksheet(name="query results")
    my_ws.write_row(0, 0, header, header_format)

    i = 1
    for r in resources.order_by("id"):
        # create the col_max column to store the length of each header
        # should be a maximum column width to 100
        col_max = [len(str(d)) if len(str(d)) <= 100 else 100 for d in header]

        j = 0
        for field in field_list:
            if "hyperlink" in field:
                my_val = f'http://dmapps{reverse("inventory:resource_detail", args=[r.id])}'
                my_ws.write_url(i, j, url=my_val, string=my_val)
            elif "people" in field:
                my_val = listrify([obj for obj in r.resource_people.all()])
                my_ws.write(i, j, str(my_val), normal_format)
            elif "keywords" in field:
                my_val = listrify([obj.non_hierarchical_name_en for obj in r.keywords.all()])
                my_ws.write(i, j, str(my_val), normal_format)
            else:
                my_val = get_field_value(r, field, nullmark="")
                my_ws.write(i, j, str(my_val), normal_format)

            # adjust the width of the columns based on the max string length in each col
            ## replace col_max[j] if str length j is bigger than stored value

            # if new value > stored value... replace stored value
            if len(str(my_val)) > col_max[j]:
                if len(str(my_val)) < 75:
                    col_max[j] = len(str(my_val))
                else:
                    col_max[j] = 75
            j += 1
        i += 1

        # set column widths
        for j in range(0, len(col_max)):
            my_ws.set_column(j, j, width=col_max[j] * 1.1)

    workbook.close()
    return target_url


def generate_open_data_resources_report(regions):
    # figure out the filename
    target_dir = os.path.join(settings.BASE_DIR, 'media', 'temp')
    target_file = "temp_data_export_{}.xlsx".format(timezone.now().strftime("%Y-%m-%d"))
    target_file_path = os.path.join(target_dir, target_file)
    target_url = os.path.join(settings.MEDIA_ROOT, 'temp', target_file)
    # create workbook and worksheets
    workbook = xlsxwriter.Workbook(target_file_path)
    # create formatting variables
    title_format = workbook.add_format(
        {'bold': False, "align": 'normal', 'font_size': 14, "text_wrap": False, 'bg_color': '#006640', 'font_color': 'white'})
    header_format = workbook.add_format(
        {'bold': False, 'border': 1, 'border_color': 'black', 'bg_color': '#A1B7BF', "align": 'normal', "text_wrap": False})

    normal_format = workbook.add_format({"align": 'left', "text_wrap": True, })
    date_format = workbook.add_format({'num_format': "yyyy-mm-dd", "align": 'left', })

    # get the resource list
    # anything with resource type as "physical collection"

    resources = models.Resource.objects.filter(Q(od_publication_date__isnull=False) | Q(fgp_publication_date__isnull=False))
    if regions and regions != "None":
        regions = regions.split(",")
        resources = resources.filter(section__division__branch__sector__region_id__in=regions)

    field_list = [
        "uuid",
        "resource_type",
        "region",
        "section",
        "title_eng",
        "status",
        "purpose_eng",
        "fgp_url",
        "public_url",
        "fgp_publication_date",
        "od_publication_date",
        "od_release_date",
        "last_revision_date",
        "people",
        "hyperlink",
    ]
    header = [get_verbose_label(resources.first(), field) for field in field_list]

    # header.append('Number of projects tagged')

    # define a worksheet
    my_ws = workbook.add_worksheet(name="query results")
    my_ws.write_row(0, 0, header, header_format)

    i = 1
    for r in resources.order_by("id"):
        # create the col_max column to store the length of each header
        # should be a maximum column width to 100
        col_max = [len(str(d)) if len(str(d)) <= 100 else 100 for d in header]

        j = 0
        for field in field_list:
            if "hyperlink" in field:
                my_val = f'http://dmapps{reverse("inventory:resource_detail", args=[r.id])}'
                my_ws.write_url(i, j, url=my_val, string=my_val)
            elif "people" in field:
                my_val = listrify([obj for obj in r.resource_people.all()])
                my_ws.write(i, j, str(my_val), normal_format)
            elif "public_url" in field:
                my_val = r.public_url
                if my_val:
                    my_ws.write_url(i, j, url=html2text(my_val).replace("\n", ""), string="link")
            elif "fgp_url" in field:
                my_val = r.fgp_url
                if my_val:
                    my_ws.write_url(i, j, url=html2text(my_val).replace("\n", ""), string="link")
            elif "keywords" in field:
                my_val = listrify([obj.non_hierarchical_name_en for obj in r.keywords.all()])
            elif "region" in field:
                my_val = str(r.section.division.branch.sector.region)
                my_ws.write(i, j, str(my_val), normal_format)
            else:
                my_val = get_field_value(r, field, nullmark="")
                my_ws.write(i, j, str(my_val), normal_format)

            # adjust the width of the columns based on the max string length in each col
            ## replace col_max[j] if str length j is bigger than stored value

            # if new value > stored value... replace stored value
            if len(str(my_val)) > col_max[j]:
                if len(str(my_val)) < 75:
                    col_max[j] = len(str(my_val))
                else:
                    col_max[j] = 75
            j += 1
        i += 1

        # set column widths
        for j in range(0, len(col_max)):
            my_ws.set_column(j, j, width=col_max[j] * 1.1)

    workbook.close()
    return target_url


def generate_custodian_report(qs):
    # figure out the filename
    target_dir = os.path.join(settings.BASE_DIR, 'media', 'temp')
    target_file = "temp_data_export_{}.xlsx".format(timezone.now().strftime("%Y-%m-%d"))
    target_file_path = os.path.join(target_dir, target_file)
    target_url = os.path.join(settings.MEDIA_ROOT, 'temp', target_file)
    # create workbook and worksheets
    workbook = xlsxwriter.Workbook(target_file_path)
    # create formatting variables
    title_format = workbook.add_format(
        {'bold': False, "align": 'normal', 'font_size': 14, "text_wrap": False, 'bg_color': '#006640', 'font_color': 'white'})
    header_format = workbook.add_format(
        {'bold': False, 'border': 1, 'border_color': 'black', 'bg_color': '#A1B7BF', "align": 'normal', "text_wrap": False})

    normal_format = workbook.add_format({"align": 'left', "text_wrap": True, })
    date_format = workbook.add_format({'num_format': "yyyy-mm-dd", "align": 'left', })

    # get the resource list
    # anything with resource type as "physical collection"

    field_list = [
        "uuid",
        "resource_type",
        "region",
        "section",
        "title_eng",
        "custodians",
        "points_of_contact|points of contact",
        "last_certification_date|date of last certification",
        "last_certification|last certification",
    ]
    header = [get_verbose_label(qs.first(), field) for field in field_list]

    # header.append('Number of projects tagged')

    # define a worksheet
    my_ws = workbook.add_worksheet(name="query results")
    my_ws.write_row(0, 0, header, header_format)

    i = 1
    for r in qs.order_by("id"):
        # create the col_max column to store the length of each header
        # should be a maximum column width to 100
        col_max = [len(str(d)) if len(str(d)) <= 100 else 100 for d in header]

        j = 0
        for field in field_list:
            if "title_eng" in field:
                my_val = r.title_eng
                my_link = f'http://dmapps{reverse("inventory:resource_detail", args=[r.id])}'
                my_ws.write_url(i, j, url=my_link, string=my_val)

            elif "custodians" in field:
                my_val = listrify([obj.person.user.email for obj in r.resource_people.filter(role__code__iexact="RI_409")], separator="; ")
                my_ws.write(i, j, str(my_val), normal_format)
            elif "points_of_contact" in field:
                my_val = nz(listrify([obj.person.user.email for obj in r.resource_people.filter(role__code__iexact="RI_414")], separator="; "), "")
                my_ws.write(i, j, str(my_val), normal_format)
            elif "region" in field:
                my_val = str(r.section.division.branch.sector.region)
                my_ws.write(i, j, str(my_val), normal_format)
            elif "last_certification_date" in field:
                my_val = "never"
                if r.last_certification:
                    my_val = r.last_certification.certification_date.strftime('%Y-%m-%d')
                my_ws.write(i, j, str(my_val), normal_format)
            elif "last_certification" in field:
                my_val = "never"
                if r.last_certification:
                    my_val = naturaltime(r.last_certification.certification_date)
                my_ws.write(i, j, str(my_val), normal_format)
            else:
                my_val = get_field_value(r, field, nullmark="")
                my_ws.write(i, j, str(my_val), normal_format)

            # adjust the width of the columns based on the max string length in each col
            ## replace col_max[j] if str length j is bigger than stored value

            # if new value > stored value... replace stored value
            if len(str(my_val)) > col_max[j]:
                if len(str(my_val)) < 75:
                    col_max[j] = len(str(my_val))
                else:
                    col_max[j] = 75
            j += 1
        i += 1

        # set column widths
        for j in range(0, len(col_max)):
            my_ws.set_column(j, j, width=col_max[j] * 1.1)

    workbook.close()
    return target_url
