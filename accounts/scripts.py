from django.contrib.auth.models import User


def resave_users():
    for u in User.objects.all():
        u.save()
