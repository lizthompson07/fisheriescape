from . import models

def resave_all(projects = models.Project.objects.all()):
    for p in projects:
        for obj in models.OMCategory.objects.all():
            if not models.OMCost.objects.filter(project=p, om_category=obj).count():
                new_item = models.OMCost.objects.create(project=p, om_category=obj)
                new_item.save()


