"""parking — Django Admin 注册"""

from django.contrib import admin
from .models import ParkingSession, Reservation, SpotConnection, ParkingSpace


@admin.register(ParkingSession)
class ParkingSessionAdmin(admin.ModelAdmin):
    list_display = ['vehicle', 'spot', 'entry_time', 'exit_time', 'amount', 'payment_status']
    list_filter = ['payment_status']
    search_fields = ['vehicle__plate_number']


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['booking_code', 'user', 'spot', 'date', 'start_time', 'status']
    list_filter = ['status', 'date']
    search_fields = ['booking_code', 'user__username']


@admin.register(SpotConnection)
class SpotConnectionAdmin(admin.ModelAdmin):
    list_display = ['from_spot', 'to_spot', 'distance']
    list_filter = ['from_spot__floor']
    search_fields = ['from_spot__space_id', 'to_spot__space_id']
    raw_id_fields = ['from_spot', 'to_spot']  # 用 ID 搜索而不是下拉（数据量大时）


@admin.register(ParkingSpace)
class ParkingSpaceAdmin(admin.ModelAdmin):
    list_display = ['space_id', 'location_name', 'node_type', 'floor', 'status', 'current_plate', 'last_updated']
    list_filter = ['node_type', 'status', 'floor', 'last_updated']
    search_fields = ['space_id', 'location_name', 'current_plate']
    list_editable = ['location_name', 'node_type']
    readonly_fields = ['created_at', 'last_updated', 'qr_code_token']
