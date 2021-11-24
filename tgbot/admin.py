import csv
import datetime

from django.contrib import admin
from django.http import HttpResponse

from .models import StorageUser, Storage, StoredThing, Orders


class StorageUserAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'telegram_id', 'username', 'first_name', 'last_name',
        'birth_date', 'DUL_series', 'DUL_number',
    ]
    search_fields = ['telegram_id', 'username', 'last_name']


class StorageAdmin(admin.ModelAdmin):
    list_display = [
        'storage_name', 'storage_address',
    ]


class StoredThingAdmin(admin.ModelAdmin):
    list_display = [
        'thing_name', 'seasonal', 'tariff1', 'tariff2', 'from_month',
    ]


def export_to_csv(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename={}.csv'.\
        format(opts.verbose_name)
    writer = csv.writer(response)
    fields = [field for field in opts.get_fields() if not field.many_to_many and not field.one_to_many]
    # Write a first row with header information
    writer.writerow([field.verbose_name for field in fields])
    # Write data rows
    for obj in queryset:
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, datetime.datetime):
                value = value.strftime('%d.%m.%Y')
            data_row.append(value)
        writer.writerow(data_row)
    return response


export_to_csv.short_description = 'Выгрузка в csv'


class OrdersAdmin(admin.ModelAdmin):
    list_display = [
        'order_num', 'order_date', 'storage', 'user', 'seasonal_store',
        'thing',
    ]
    list_filter = ['storage']
    fields = [
        'order_date', 'storage', 'user', 'seasonal_store', 'thing',
        'other_type_size', 'seasonal_things_count', 'store_duration',
        'store_duration_type', 'summa'
    ]
    actions = [export_to_csv]


admin.site.register(StorageUser, StorageUserAdmin)
admin.site.register(Storage, StorageAdmin)
admin.site.register(StoredThing, StoredThingAdmin)
admin.site.register(Orders, OrdersAdmin)
