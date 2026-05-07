"""
devices — API 视图

端点清单：
- GET    /api/v1/devices/list/                    设备列表
- GET    /api/v1/devices/list/{id}/               设备详情
- POST   /api/v1/devices/list/                    [管理端] 添加设备
- PUT    /api/v1/devices/list/{id}/               [管理端] 更新设备
- DELETE /api/v1/devices/list/{id}/               [管理端] 删除设备
- GET    /api/v1/devices/list/overview/           设备概览统计
- POST   /api/v1/devices/list/{id}/report-fault/  报告故障
"""

from django.db.models import Count, Q, Avg
from django.utils import timezone
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Device
from .serializers import DeviceSerializer, DeviceListSerializer


class DeviceViewSet(viewsets.ModelViewSet):
    """
    设备管理 — 对应 _11 设备管理页面

    仅管理员可增删改，所有登录用户可查看
    """
    queryset = Device.objects.all()
    filterset_fields = ['device_type', 'status']
    search_fields = ['name', 'serial_number', 'location']
    ordering_fields = ['name', 'status', 'uptime']

    def get_serializer_class(self):
        """列表用精简版，详情用完整版"""
        if self.action == 'list':
            return DeviceListSerializer
        return DeviceSerializer

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=['get'], url_path='overview')
    def overview(self, request):
        """
        设备概览 — 对应 _11 顶部统计卡片

        GET /api/v1/devices/list/overview/
        返回：
        - total: 总设备数 → "总计 124"
        - online: 在线数 → "已连接 118 在线"
        - faults: 故障数 → "活动故障 6 严重"
        - maintenance: 维护计划 → "计划维护 12 本周"
        - avg_latency: 平均延迟 → "网络延迟 24ms"
        """
        qs = Device.objects.all()
        stats = qs.aggregate(
            total=Count('id'),
            online=Count('id', filter=Q(status=Device.Status.ONLINE)),
            faults=Count('id', filter=Q(status=Device.Status.ERROR)),
            maintenance=Count('id', filter=Q(status=Device.Status.MAINTENANCE)),
            avg_uptime=Avg('uptime'),
        )
        return Response(stats)

    @action(detail=True, methods=['post'], url_path='report-fault')
    def report_fault(self, request, pk=None):
        """
        报告故障 — 对应 _11 故障卡片的 "报告故障" 按钮

        POST /api/v1/devices/list/{id}/report-fault/
        body: { fault_detail: "信号丢失" }
        """
        device = self.get_object()
        fault_detail = request.data.get('fault_detail', '')
        if not fault_detail:
            return Response(
                {'detail': '请提供故障描述'},
                status=400
            )
        device.status = Device.Status.ERROR
        device.fault_detail = fault_detail
        device.save(update_fields=['status', 'fault_detail', 'updated_at'])
        serializer = DeviceSerializer(device)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='restart')
    def restart(self, request, pk=None):
        """
        重启/恢复设备

        POST /api/v1/devices/list/{id}/restart/
        body: { type: "soft" | "hard" | "recover" }
        """
        device = self.get_object()
        restart_type = request.data.get('type', 'soft')

        if restart_type == 'recover':
            # 恢复设备到在线状态
            device.status = Device.Status.ONLINE
            device.fault_detail = ''
            device.offline_since = None
            device.save(update_fields=['status', 'fault_detail', 'offline_since', 'updated_at'])
            serializer = DeviceSerializer(device)
            return Response(serializer.data)

        if restart_type == 'hard':
            device.status = Device.Status.OFFLINE
            device.offline_since = timezone.now()
            device.save(update_fields=['status', 'offline_since', 'updated_at'])
            return Response({'detail': '硬件重启中，设备已离线'})
        # 软重启：短暂离线后自动恢复
        device.status = Device.Status.MAINTENANCE
        device.save(update_fields=['status', 'updated_at'])
        return Response({'detail': '软重启信号已发送，设备即将重新连接'})
