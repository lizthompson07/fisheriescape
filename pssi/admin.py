from django.contrib import admin
from pssi.models import DataAsset, Tag, BusinessGlossary, DataGlossary, Comment, Acronym


# Register your models here.
# Any model you register here will show up in DMApps admin tools (top left of screen when on localhost)
# NOTE: These models are currently registered to test if data ingestion is working - when pushing to DMApps, make sure only the necessary models are registered

admin.site.register(DataAsset)
admin.site.register(Tag)
admin.site.register(DataGlossary)
admin.site.register(BusinessGlossary)
admin.site.register(Comment)
admin.site.register(Acronym)