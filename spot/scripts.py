from . import models

def resave_all_projects():
    for obj in models.Project.objects.all():
        obj.save()
