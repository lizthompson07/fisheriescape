from django.contrib import admin
from . import models
# Register your models here.

admin.site.register(models.Person)
admin.site.register(models.RequestType)
admin.site.register(models.Section)
admin.site.register(models.ServiceDeskTicket)
admin.site.register(models.Tag)
admin.site.register(models.Ticket)
admin.site.register(models.File)
