from django.contrib import admin
from whalebrary.models import Size, Status, Organisation, Training, Order
import datetime

# Register your models here.
admin.site.register(Size)
admin.site.register(Status)
admin.site.register(Organisation)
admin.site.register(Training)

# custom function to bulk mark received the selected orders in django admin for Order model


def mark_received(modeladmin, request, queryset):
    queryset.update(date_received=datetime.datetime.now())
    mark_received.short_description = "Mark selected items as Received"


class OrderAdmin(admin.ModelAdmin):
    list_display = ['item', 'quantity', 'cost', 'date_ordered']
    ordering = ['item']
    actions = [mark_received]


admin.site.register(Order, OrderAdmin)