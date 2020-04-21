def csas_authorized(user):
    return user.is_authenticated and (user.groups.filter(name='csas_user').exists() or
                                      csas_admin(user))


def csas_admin(user):
    return user.is_authenticated and user.groups.filter(name='csas_admin').exists()
