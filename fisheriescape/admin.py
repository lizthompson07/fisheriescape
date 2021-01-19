from django.contrib.gis import admin
from .models import FisheryArea

admin.site.register(FisheryArea, admin.GeoModelAdmin)
