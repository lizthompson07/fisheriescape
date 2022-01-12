def is_admin(user):
    if user:
        return bool(hasattr(user, "spot_user") and user.spot_user.is_admin)


def is_crud_user(user):
    # nested under admin
    if user:
        return is_admin(user) or bool(hasattr(user, "spot_user") and user.spot_user.is_crud_user)


def has_read_only(user):
    if user:
        return bool(hasattr(user, "spot_user"))
