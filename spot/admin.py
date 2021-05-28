from django.contrib import admin
from . import models


class SpotAdminSite(admin.AdminSite):
    site_header = "Spot Admin Site"
    site_title = "Spot Admin Portal"
    index_title = "Welcome to Spot Site Admin"


spot_admin_site = SpotAdminSite("spot_admin")

spot_admin_site.register(models.DataSubType)
