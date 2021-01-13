

def bio_diverisity_authorized(user):
    # return user.is_authenticated and user.groups.filter(name='bio_diversity_admin').exists()
    return user.groups.filter(name='bio_diversity_admin').exists()
