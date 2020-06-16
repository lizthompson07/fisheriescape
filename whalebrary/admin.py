from django.contrib import admin
from whalebrary.models import Size, Status, Organisation, Training, Transaction

# Register your models here.
admin.site.register(Size)
admin.site.register(Status)
admin.site.register(Organisation)
admin.site.register(Training)

# custom function to bulk change status to 'on hand' in django admin for Transaction model

def mark_on_hand(modeladmin, request, queryset):
    queryset.update(status='1')
mark_on_hand.short_description = "Mark selected items as On Hand"

class TransactionAdmin(admin.ModelAdmin):
    list_display = ['item', 'quantity', 'status']
    ordering = ['item']
    actions = [mark_on_hand]

admin.site.register(Transaction, TransactionAdmin)