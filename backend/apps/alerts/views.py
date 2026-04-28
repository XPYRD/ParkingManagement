"""
alerts — API 视图

端点清单：
- GET    /api/v1/alerts/alerts/                   预警列表
- GET    /api/v1/alerts/alerts/{id}/              预警详情
- POST   /api/v1/alerts/alerts/                   [管理端] 创建预警
- PATCH  /api/v1/alerts/alerts/{id}/              [管理端] 更新预警状态
- GET    /api/v1/alerts/alerts/stats/             预警统计
- PATCH  /api/v1/alerts/alerts/{id}/resolve/      标记已解决
- GET    /api/v1/alerts/tickets/                  工单列表
- POST   /api/v1/alerts/tickets/                  提交工单
- GET    /api/v1/alerts/tickets/{id}/             工单详情
"""

from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Alert, Ticket
from .serializers import AlertSerializer, TicketSerializer


class AlertViewSet(viewsets.ModelViewSet):
    """
    系统预警 — 对应 _7 告警表格 + center 预警Feed

    仅管理员可访问
    """
    serializer_class = AlertSerializer
    queryset = Alert.objects.all()
    permission_classes = [permissions.IsAdminUser]
    filterset_fields = ['alert_type', 'severity', 'status']
    search_fields = ['title', 'location']
    ordering_fields = ['created_at', 'severity']

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        """
        预警统计 — 对应 center 顶部统计卡

        GET /api/v1/alerts/alerts/stats/
        返回：
        - pending_count → "未处理威胁 12"
        - investigating_count → "调查中"
        - emergency_count → "紧急事件"
        - resolved_today → "今日已解决"
        """
        qs = Alert.objects.all()
        today = timezone.now().date()
        stats = qs.aggregate(
            pending_count=Count('id', filter=Q(status=Alert.Status.PENDING)),
            investigating_count=Count('id', filter=Q(status=Alert.Status.INVESTIGATING)),
            emergency_count=Count('id', filter=Q(severity=Alert.Severity.EMERGENCY)),
            resolved_today=Count('id', filter=Q(
                status=Alert.Status.RESOLVED,
                resolved_at__date=today,
            )),
        )
        return Response(stats)

    @action(detail=True, methods=['post'], url_path='resolve')
    def resolve(self, request, pk=None):
        """
        标记预警已解决 — 对应 center Feed 的操作按钮

        POST /api/v1/alerts/alerts/{id}/resolve/
        """
        alert = self.get_object()
        alert.status = Alert.Status.RESOLVED
        alert.resolved_at = timezone.now()
        alert.save(update_fields=['status', 'resolved_at'])
        return Response({'detail': '预警已标记为已解决', 'status': alert.status})


class TicketViewSet(viewsets.ModelViewSet):
    """
    用户工单 — 对应 _12 故障/投诉反馈

    用户端：提交工单 + 查看自己的工单
    管理端：查看所有工单 + 更新状态
    """
    serializer_class = TicketSerializer
    filterset_fields = ['ticket_type', 'status']
    search_fields = ['ticket_id', 'title']
    ordering_fields = ['created_at', 'status']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Ticket.objects.all()
        return Ticket.objects.filter(user=user)

    def get_permissions(self):
        """
        用户可以创建和查看自己的工单；
        管理员可以更新状态（审核/关闭）
        """
        if self.action == 'destroy':
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]
