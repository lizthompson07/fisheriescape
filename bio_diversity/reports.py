import os

from openpyxl import load_workbook

from bio_diversity import models
from dm_apps import settings


def generate_facility_tank_report(facic_id):
    # figure out the filename
    target_dir = os.path.join(settings.BASE_DIR, 'media', 'temp')
    target_file = "temp_export.xlsx"
    target_file_path = os.path.join(target_dir, target_file)
    target_url = os.path.join(settings.MEDIA_ROOT, 'temp', target_file)

    template_file_path = os.path.join(settings.BASE_DIR, 'bio_diversity', 'static', "report_templates", "facility_tank_template.xlsx")

    facic = models.FacilityCode.objects.filter(pk=facic_id).get()

    # get all project years that are not in the following status: draft, not approved, cancelled
    # and that are a part of a project whose default funding source has an english name containing "csrf"
    qs = models.Tank.objects.filter(facic_id=facic)

    wb = load_workbook(filename=template_file_path)

    # to order workshees so the first sheet comes before the template sheet, rename the template and then copy the
    # renamed sheet, then rename the copy to template so it exists for other sheets to be created from
    ws = wb['template']
    ws.title = facic.name
    wb.copy_worksheet(ws).title = str("template")
    try:
        ws = wb[facic.name]
    except KeyError:
        print(facic.name, "is not a valid name of a worksheet")

    # start writing data at row 3 in the sheet
    row_count = 3
    for item in qs:

        ws['A' + str(row_count)].value = item.name

        row_count += 1

    wb.save(target_file_path)

    return target_url