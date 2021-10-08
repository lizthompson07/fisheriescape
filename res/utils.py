import math

from django.contrib.auth.models import Group


# open basic access up to anybody who is logged in
def in_res_admin_group(user):
    # make sure the following group exist:
    admin_group, created = Group.objects.get_or_create(name="res_admin")
    if user:
        return admin_group in user.groups.all()


def in_res_crud_group(user):
    # make sure the following group exist:
    crud_group, created = Group.objects.get_or_create(name="res_crud")
    if user:
        return in_res_admin_group(user) or crud_group in user.groups.all()

