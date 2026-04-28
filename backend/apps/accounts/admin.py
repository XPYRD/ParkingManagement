"""accounts — Django Admin 注册"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Vehicle


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """用户管理 — 在 Django Admin 中扩展显示字段"""
    list_display = ['username', 'phone', 'is_vip', 'status', 'is_staff', 'date_joined']
    list_filter = ['status', 'is_vip', 'is_staff', 'is_active']
    search_fields = ['username', 'phone', 'email']
    # 在编辑表单中增加自定义字段
    fieldsets = BaseUserAdmin.fieldsets + (
        ('扩展信息', {'fields': ('phone', 'avatar', 'is_vip', 'status')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('扩展信息', {'fields': ('phone',)}),
    )


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['plate_number', 'brand', 'model', 'owner', 'is_primary', 'created_at']
    list_filter = ['brand', 'is_primary']
    search_fields = ['plate_number', 'owner__username']
