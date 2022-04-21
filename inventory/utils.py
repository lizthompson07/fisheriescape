from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404

from . import models


def is_nat_admin(user):
    if user:
        return bool(hasattr(user, "inventory_user") and user.inventory_user.is_admin)


def is_regional_admin(user):
    if user:
        return bool(hasattr(user, "inventory_user") and user.inventory_user.region)


def is_admin(user):
    return is_nat_admin(user) or is_regional_admin(user)


def is_custodian_or_admin(user, resource_id):
    """returns True if user is a "custodian" in the specified resource"""
    resource = get_object_or_404(models.Resource, pk=resource_id)

    if user.id:
        # first, check to see if user is a national admin
        if is_nat_admin(user):
            return True
        elif is_regional_admin(user) and resource.section and resource.section.division.branch.sector.region == user.inventory_user.region:
            return True
        else:
            # if the user has no associated Person in the app, automatic fail
            try:
                person = get_object_or_404(models.Person, user=user)
            except ObjectDoesNotExist:
                return False
            else:
                # check to see if they are listed as custodian (role_id=1) on the specified resource id
                # custodian (1); principal investigator (2); data manager (8); steward (19); author (13); owner (10)
                return models.ResourcePerson.objects.filter(person=person, resource=resource_id,
                                                            role_id__in=[1, 2, 8, 19, 13, 10]).count() > 0
