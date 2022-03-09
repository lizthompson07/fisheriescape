from django.contrib.gis import admin
from .models import FisheryArea, MarineMammal, Week, Hexagon, Score, Mitigation

admin.site.register(FisheryArea, admin.GeoModelAdmin)
admin.site.register(MarineMammal, admin.ModelAdmin)
admin.site.register(Week, admin.ModelAdmin)
admin.site.register(Hexagon, admin.ModelAdmin)
admin.site.register(Score, admin.ModelAdmin)
admin.site.register(Mitigation, admin.ModelAdmin)
