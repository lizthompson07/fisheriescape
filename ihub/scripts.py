from . import models
from masterlist import models as shared_models

def resave_all(entries = models.Entry.objects.all()):
    for obj in entries:
        obj.save()

def ihub_vetted():
    for person in shared_models.Person.objects.filter(last_modified_by_id__isnull=False):
        if person.last_modified_by_id == 500 or person.last_modified_by_id == 443:
            person.ihub_vetted = True
            person.save()

