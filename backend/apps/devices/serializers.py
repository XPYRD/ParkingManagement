"""
devices — 序列化器

前后端字段对齐：Device → _11 设备卡片
"""

from rest_framework import serializers
from .models import Device


class DeviceSerializer(serializers.ModelSerializer):
    """
    设备信息 — 对应 _11 设备管理卡片

    卡片字段 → 映射：
    - 标题 → name
    - 副标题(位置) → location
    - 状态标签 → status / status_label
    - 图标类型 → device_type / device_type_label
    - 详情行 → serial_number, uptime, last_maintenance
    - 故障信息 → fault_detail, offline_since
    """

    status_label = serializers.CharField(
        source='get_status_display', read_only=True
    )
    device_type_label = serializers.CharField(
        source='get_device_type_display', read_only=True
    )

    class Meta:
        model = Device
        fields = [
            'id', 'name', 'device_type', 'device_type_label',
            'location', 'serial_number',
            'status', 'status_label', 'uptime',
            'last_maintenance', 'fault_detail', 'offline_since',
            'paper_level', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DeviceListSerializer(serializers.ModelSerializer):
    """
    设备列表（精简版） — 用于统计卡片的下拉列表或地图标记

    只返回核心字段，减少网络传输量
    """

    status_label = serializers.CharField(
        source='get_status_display', read_only=True
    )

    class Meta:
        model = Device
        fields = [
            'id', 'name', 'device_type', 'location',
            'status', 'status_label',
        ]
