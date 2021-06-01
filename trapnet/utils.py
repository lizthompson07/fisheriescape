
def is_admin(user):
    if user:
        return user.groups.filter(name='trapnet_admin').count() != 0


def can_access(user):
    if user:
        return is_admin(user) or user.groups.filter(name='trapnet_access').exists()

