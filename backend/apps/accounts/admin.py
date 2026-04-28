"""accounts — Django Admin 注册"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Vehicle


def _remove_user_permissions(fieldsets):
    cleaned = []
    for title, options in fieldsets:
        fields = options.get('fields', ())
        if isinstance(fields, (tuple, list)):
            options = {**options, 'fields': tuple(f for f in fields if f != 'user_permissions')}
        cleaned.append((title, options))
    return tuple(cleaned)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """用户管理 — 在 Django Admin 中扩展显示字段"""
    list_display = ['username', 'phone', 'is_vip', 'status', 'is_staff', 'date_joined']
    list_filter = ['status', 'is_vip', 'is_staff', 'is_active']
    search_fields = ['username', 'phone', 'email']
    # 在编辑表单中增加自定义字段
    fieldsets = _remove_user_permissions(BaseUserAdmin.fieldsets) + (
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
