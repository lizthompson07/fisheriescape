def is_grais_admin(user):
    if user:
        return bool(hasattr(user, "grais_user") and user.grais_user.is_admin)


def has_grais_crud(user):
    # nested under admin
    if user:
        return is_grais_admin(user) or bool(hasattr(user, "grais_user") and user.grais_user.is_crud_user)


def has_grais_access(user):
    # nested under admin
    if user:
        return bool(hasattr(user, "grais_user"))
