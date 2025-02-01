from django.contrib import admin

from nadejda_94_django.records.models import Record, Order, Partner


@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = ('pk', 'created_at', 'warehouse', 'order_type', 'amount', 'order', 'note')
    search_fields = ('pk',)
    list_filter = ('partner__name',)
    ordering = ('pk',)


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'type', 'balance')
    search_fields = ('name',)
    list_filter = ('name',)
    ordering = ('pk',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('month', 'al_counter', 'glass_counter', 'pvc_counter')