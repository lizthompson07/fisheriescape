from django.contrib.gis import admin
from .models import FisheryArea, MarineMammal, Week

admin.site.register(FisheryArea, admin.GeoModelAdmin)
admin.site.register(MarineMammal, admin.ModelAdmin)
admin.site.register(Week, admin.ModelAdmin)
