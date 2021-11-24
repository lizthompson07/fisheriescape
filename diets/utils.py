def is_admin(user):
    if user:
        return bool(hasattr(user, "diets_user") and user.diets_user.is_admin)


def is_crud_user(user):
    # nested under admin
    if user:
        return is_admin(user) or bool(hasattr(user, "diets_user") and user.diets_user.is_crud_user)


def can_read(user):
    # nested under admin and crud
    if user:
        return is_admin(user) or is_crud_user(user) or hasattr(user, "diets_user")
