# open basic access up to anybody who is logged in

def in_scuba_admin_group(user):
    if user:
        return user.groups.filter(name='scuba_admin').exists()


def in_scuba_crud_group(user):
    if user:
        return in_scuba_admin_group(user) or user.groups.filter(name='scuba_crud').exists()
