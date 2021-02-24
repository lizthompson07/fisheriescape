from django.contrib import admin

# Register your models here.
from vault.models import Region, Purpose, Certainty, Sex, LifeStage, HealthStatus, IndividualIdentification

admin.site.register(Region)
admin.site.register(Purpose)
admin.site.register(Certainty)
admin.site.register(Sex)
admin.site.register(LifeStage)
admin.site.register(HealthStatus)
admin.site.register(IndividualIdentification)
