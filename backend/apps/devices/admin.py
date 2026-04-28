"""devices — Django Admin 注册"""

from django.contrib import admin
from .models import Device


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['name', 'device_type', 'location', 'status', 'uptime', 'last_maintenance']
    list_filter = ['device_type', 'status']
    search_fields = ['name', 'serial_number', 'location']
