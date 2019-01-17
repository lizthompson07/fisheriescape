from . import models

# def resave_all(resources = models.Resource.objects.all()):
#
#     for r in resources:
#         if r.uuid == None:
#             my_r = models.Resource.objects.get(id=r.id)
#             my_r.save()


# def resave_all(people = models.Person.objects.all()):
#
#     for p in people:
#         my_p = models.Person.objects.get(user_id=p.user.id)
#         my_p.save()
#

def resave_all(keywords = models.Keyword.objects.all()):

    for k in keywords:
        my_obj = models.Keyword.objects.get(id=k.id)
        my_obj.save()
