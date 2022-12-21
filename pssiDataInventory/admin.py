from django.contrib import admin
from pssiDataInventory.models import DataAsset, Tag, BusinessGlossary, DataGlossary, Comment, Acronym


# Register your models here.
# Any model you register here will show up in DMApps admin tools (top left of screen when on localhost)
admin.site.register(DataAsset)
admin.site.register(Tag)
admin.site.register(DataGlossary)
#admin.site.register(BusinessGlossary)
admin.site.register(Comment)
admin.site.register(Acronym)