def can_read(user):
    if user:
        return bool(hasattr(user, "herring_user"))


def is_admin(user):
    if user:
        return bool(can_read(user) and user.herring_user.is_admin)


def is_crud_user(user):
    # nested under admin
    if user:
        return is_admin(user) or bool(can_read(user) and user.herring_user.is_crud_user)
