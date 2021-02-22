from django.contrib import admin

# Register your models here.
from vault.models import Region, Purpose

admin.site.register(Region)
admin.site.register(Purpose)
