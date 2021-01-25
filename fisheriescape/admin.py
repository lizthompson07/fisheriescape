from django.contrib.gis import admin
from .models import FisheryArea, MarineMammals

admin.site.register(FisheryArea, admin.GeoModelAdmin)
admin.site.register(MarineMammals, admin.ModelAdmin)
