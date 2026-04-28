"""
alerts — 序列化器

前后端字段对齐：
- Alert → _7 告警表格 + center 预警Feed
- Ticket → _12 工单卡片列表
"""

from rest_framework import serializers
from .models import Alert, Ticket


class AlertSerializer(serializers.ModelSerializer):
    """
    系统预警 — 对应 center 预警Feed + _7 告警表格

    Feed 卡片字段 → 映射：
    - 图标类型 → alert_type / alert_type_label
    - 标题 → title
    - 描述 → detail
    - 位置 → location
    - 严重程度标签 → severity / severity_label
    - 状态 → status / status_label
    - 时间 → created_at
    """

    alert_type_label = serializers.CharField(
        source='get_alert_type_display', read_only=True
    )
    severity_label = serializers.CharField(
        source='get_severity_display', read_only=True
    )
    status_label = serializers.CharField(
        source='get_status_display', read_only=True
    )

    class Meta:
        model = Alert
        fields = [
            'id', 'alert_type', 'alert_type_label',
            'title', 'detail', 'location',
            'severity', 'severity_label',
            'status', 'status_label',
            'resolved_at', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class TicketSerializer(serializers.ModelSerializer):
    """
    用户工单 — 对应 _12 工单列表

    卡片字段 → 映射：
    - 编号 → ticket_id
    - 类型 → ticket_type / ticket_type_label
    - 标题 → title
    - 描述 → description
    - 状态标签 → status / status_label
    - 提交时间 → created_at
    """

    ticket_type_label = serializers.CharField(
        source='get_ticket_type_display', read_only=True
    )
    status_label = serializers.CharField(
        source='get_status_display', read_only=True
    )
    username = serializers.CharField(
        source='user.username', read_only=True
    )

    class Meta:
        model = Ticket
        fields = [
            'id', 'user', 'username', 'ticket_id',
            'ticket_type', 'ticket_type_label',
            'title', 'description', 'attachment',
            'status', 'status_label',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user', 'ticket_id', 'created_at', 'updated_at']

    def create(self, validated_data: dict) -> Ticket:
        """创建工单时自动关联用户 + 生成工单编号"""
        import random
        validated_data['user'] = self.context['request'].user
        validated_data['ticket_id'] = f'ST-{random.randint(1000, 9999)}'
        return super().create(validated_data)
