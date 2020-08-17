from django.contrib import admin
from . import models


@admin.register(models.Organization)
class OrganizationAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("legal_name",)}


@admin.register(models.Individual)
class ContactAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("first_name", "last_name")}
