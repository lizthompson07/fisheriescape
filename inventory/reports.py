import shutil

import xlsxwriter as xlsxwriter
from django.template.defaultfilters import yesno
from django.utils import timezone
from django.conf import settings
from django.utils.translation import gettext as _

from lib.functions.custom_functions import listrify
from lib.templatetags.verbose_names import get_verbose_label
from . import models
from . import xml_export
import os


def generate_batch_xml(sections):
    # figure out the filenames etc..
    #################################
    # this will be the target dir of the zipfile
    zip_dir = os.path.join(settings.BASE_DIR, 'media', 'inventory', 'temp')
    # this is the filename for the zip file
    zip_filename = "temp_export_{}".format(timezone.now().strftime("%Y-%m-%d"))
    # this is the full path to the target zip file
    zip_file_path = os.path.join(zip_dir, zip_filename)
    # this is the url to the target zip file.. is what is returned by the function
    target_url = os.path.join(settings.MEDIA_ROOT, 'inventory', 'temp', zip_filename)
    # this will be the target dir of the xml files
    xml_dir = os.path.join(settings.BASE_DIR, 'media', 'inventory', 'temp', 'zipdir')


    # clean out the zip_dir directory
    for root, dirs, files in os.walk(zip_dir):
        for file in files:
            os.remove(file)

    # start with all resources
    resource_list = models.Resource.objects.all()
    # parse out the sections arg and refine the list
    if sections != "None":
        section_list = [models.Section.objects.get(pk=int(obj)) for obj in sections.split(",")]
        resource_list = [resource for resource in resource_list if resource.section in section_list]

    # generate an xml file for each resource in resource_list
    for resource in resource_list:
        # get the xml data
        xml_data = xml_export.construct(resource, pretty=False)
        # figure out the filename
        xml_filename = "xml_metadata_export_{}.xml".format(resource.id)
        target_file_path = os.path.join(xml_dir, xml_filename)
        # write xml data to file
        print(resource.id)
        xml_data.write(target_file_path)

    # zip the folder
    # adapted from https://stackoverflow.com/questions/1855095/how-to-create-a-zip-archive-of-a-directory
    shutil.make_archive(zip_file_path, 'zip', xml_dir)

    return target_url


def export_resource_xml(request, resource, publish):
    # grab resource instance
    my_resource = models.Resource.objects.get(pk=resource)

    if publish == "yes":
        my_resource.fgp_publication_date = timezone.now()
        my_resource.flagged_4_publication = False

        my_resource.save()

    # Create the HttpResponse object
    filename = "xml_metadata_export_{}.xml".format(my_resource.id)
    response = HttpResponse(content_type='text/xml')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)

    # pass the object to the xml builder module
    xml_data = xml_export.construct(my_resource)

    response.write(xml_data)
    # print(xml_data)
    return response
    #
