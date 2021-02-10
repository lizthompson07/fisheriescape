from typing import List

from csas.models import CohHonorific, LanLanguage, CotType, NotNotificationPreference, SecSector, RolRole
from csas import models

###################################################################################################
# To run this script start the django shell:
#   >python manage.py shell
#
# Import the script:
#   >from csas.scripts import data_load_special
###################################################################################################


# load_lookup loads options into a model. Presumably the model is a simple lookup table with an auto generated ID field
# and a name field. The method will check to see if a name already exists in the lookup and will not add an options
# if it already exists
def load_lookup(model, options):
    for opt in options:
        # filter the model looking for this option. The option is only added if the filter returns a NoneType object
        if not model.objects.filter(name=opt[0]):
            model(name=opt[0], nom=opt[1]).save()


# --------------------------------------------------------------------------------------------------------------
# Yongcun Hu: Add some special terms to the drop down manual, they were extracted from the historical data by
#             Tobias, he needs them to load the historical data into the database.
#
#
# Load Process Types
# process = [['Advisory Meeting ', ' Advisory Meeting(fr)'], ['Science Response ', ' Science Response(fr)'],
#            ['Frameworks ', ' Frameworks(fr)']]
process = [['Regional Peer Review', 'Regional Peer Review(fr)'],
           ['National Peer Review', 'National Peer Review(fr)'],
           ['Regional Science Response Process (SRP)', 'Regional Science Response Process (SRP)(fr)']]
load_lookup(models.AptAdvisoryProcessType, process)

# load Series
# series = [['SAR ', ' SAR(fr)'], ['SR ', ' SR(fr)'], ['RES ', ' RES(fr)'], ['PRO ', ' PRO(fr)']]
series = [['SAR-AS', 'SAR-AS(fr)'],
          ['SRR-RS', 'SRR-RS(fr)']]
load_lookup(models.PsePublicationSeries, series)

# load Publication Status
# pub_status = [['In Approvals ', ' In Approvals(fr)'], ['Submitted for Posting ', ' Submitted for Posting(fr)']]
pub_status = [['Not Yet Submitted', 'Not Yet Submitted(fr)'],
              ['Published', 'Published(fr)']]
load_lookup(models.PusPublicationStatus, pub_status)
# --------------------------------------------------------------------------------------------------------------

print("Data Load Special complete")
