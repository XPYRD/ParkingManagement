"""alerts — Django Admin 注册"""

from django.contrib import admin
from .models import Alert, Ticket


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['title', 'alert_type', 'severity', 'status', 'location', 'created_at']
    list_filter = ['alert_type', 'severity', 'status']
    search_fields = ['title', 'location']


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['ticket_id', 'user', 'ticket_type', 'title', 'status', 'created_at']
    list_filter = ['ticket_type', 'status']
    search_fields = ['ticket_id', 'title', 'user__username']
