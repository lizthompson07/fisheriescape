def csas_authorized(user):
    return user.is_authenticated and user.groups.filter(name='csas_admin').exists()