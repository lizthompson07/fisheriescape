import math

from django.contrib.auth.models import Group
# open basic access up to anybody who is logged in
from django.utils.translation import gettext as _


def in_csas_admin_group(user):
    # make sure the following group exist:
    admin_group, created = Group.objects.get_or_create(name="csas2_admin")
    if user:
        return admin_group in user.groups.all()


def in_csas_crud_group(user):
    # make sure the following group exist:
    crud_group, created = Group.objects.get_or_create(name="csas2_crud")
    if user:
        return in_csas_admin_group(user) or crud_group in user.groups.all()



def get_sample_field_list():
    my_list = [
        'datetime',
        'site_description',
        'site_identifier',
        'collector',
        'sample_identifier',
        'latitude',
        'longitude',
        'comments',
    ]
    return my_list


def get_collection_field_list(collection):
    my_list = [
        'name',
        'program_description',
        'region',
        'location_description',
        'province',
        'contacts',
        'dates|dates',
        'tags',
        'metadata|{}'.format(_("metadata")),
    ]
    while None in my_list: my_list.remove(None)
    return my_list


def get_batch_field_list():
    my_list = [
        'id',
        'datetime',
        'operators',
        'comments',
    ]
    return my_list
