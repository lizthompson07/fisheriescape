def is_regional_admin(user):
    if user.id:
        return bool(hasattr(user, "cars_user") and user.cars_user.region)


def is_national_admin(user):
    if user:
        return bool(hasattr(user, "cars_user") and user.cars_user.is_admin)


def is_admin(user):
    if user:
        return is_national_admin(user) or is_regional_admin(user)
