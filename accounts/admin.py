from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Group

from . import models

# Register your models here.

admin.site.register(models.Announcement)
admin.site.register(models.Profile)

# useful tip from:
# https://stackoverflow.com/questions/34568311/show-group-members-in-django-admin

admin.site.unregister(Group)


class UserInLine(admin.TabularInline):
    model = Group.user_set.through
    extra = 0


@admin.register(Group)
class GenericGroup(GroupAdmin):
    inlines = [UserInLine]
