from django.utils.translation import gettext as _


def is_regional_admin(user):
    if user.id:
        return bool(hasattr(user, "cars_user") and user.cars_user.region)


def is_national_admin(user):
    if user:
        return bool(hasattr(user, "cars_user") and user.cars_user.is_admin)


def is_admin(user):
    if user:
        return is_national_admin(user) or is_regional_admin(user)


def can_modify_vehicle(user, vehicle, return_as_dict=False):
    """
    returns True if user has permissions to delete or modify a vehicle
    """
    my_dict = dict(is_allowed=False, reason=_("You are not logged in"))

    if user.id:
        my_dict["reason"] = _("You do not have the permissions to modify this process")
        # are they a national administrator?
        if is_national_admin(user):
            my_dict["reason"] = _("You can modify this vehicle because you are a national app administrator")
            my_dict["is_allowed"] = True
        # are they a regional administrator?
        elif is_regional_admin(user) and user.csas_user.region == vehicle.region:
            my_dict["reason"] = _("You can modify this vehicle because you are an administrator to the region to which it belongs")
            my_dict["is_allowed"] = True
        elif user == vehicle.custodian:
            my_dict["reason"] = _("You are the custodian for this vehicle")
            my_dict["is_allowed"] = True
        return my_dict if return_as_dict else my_dict["is_allowed"]
