from csas.models import CohHonorific, LanLanguage, CotType, NotNotificationPreference, SecSector, RolRole

###################################################################################################
# To run this script start the django shell:
#   >python manage.py shell
#
# Import the script:
#   >from csas.scripts import data_load
###################################################################################################


# load_lookup loads options into a model. Presumably the model is a simple lookup table with an auto generated ID field
# and a name field. The method will check to see if a name already exists in the lookup and will not add an options
# if it already exists
def load_lookup(model, options):

    for opt in options:
        # filter the model looking for this option. The option is only added if the filter returns a NoneType object
        if not model.objects.filter(name=opt):
            model(name=opt).save()


# Load the honorific model
honorifics = ['Mr.', 'Mrs.', 'Ms.', 'Dr.', 'Chief', 'Capt.']
load_lookup(CohHonorific, honorifics)

# --> Ask Tana if languages can be represented with one letter. I know there is some indigenous languages to add as well
# --> Till then language population is commented out
# Load the language model
languages = ['E', 'F']
# load_lookup(LanLanguage, languages)

# Load the contact type model
types = ['Government', 'Industry', 'NGO', 'Indigenous', 'Consultant', 'Contractor']
load_lookup(CotType, types)

# Load the notification preferences model
preferences = ['Phone', 'Email', 'Fax']
load_lookup(NotNotificationPreference, preferences)

# Load Sector model
sectors = ['Science', 'Oceans', 'FFHPP', 'SARA', 'RM', 'AMD']
load_lookup(SecSector, sectors)

# Load the role model
roles = ['Regional Coordinator', 'Regional Science Advisor', 'Regional Admin', 'Director']
load_lookup(RolRole, roles)