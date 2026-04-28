"""
dashboard — 管理后台仪表盘聚合 API

对应 _7 管理后台首页：
- 日营收、空间占用率、系统运行状况、近期告警
- 这里不单独建 Model，而是聚合查询其他 App 的数据
"""

from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from parking.models import ParkingSpace, ParkingSession
from payments.models import Payment
from devices.models import Device


class DashboardOverviewView(APIView):
    """
    仪表盘总览 — 对应 _7 管理后台首页

    GET /api/v1/dashboard/overview/

    返回 _7 页面中的所有统计数据：
    - 日营收 → daily_revenue
    - 空间占用率 → occupancy
    - 系统健康度 → system_health
    - 近期告警 → recent_alerts
    - 今日流量 → today_traffic
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        today = timezone.now().date()

        # 1. 日营收 — 对应 _7 "日营收 ¥X" 卡片
        daily_revenue = Payment.objects.filter(
            status=Payment.Status.SUCCESS,
            created_at__date=today,
        ).aggregate(total=Sum('amount'))['total'] or 0

        # 2. 空间占用率 — 对应 _7 "空间占用率 84%" 饼图
        spot_stats = ParkingSpace.objects.aggregate(
            total=Count('id'),
            occupied=Count('id', filter=~(Q(current_plate__isnull=True) | Q(current_plate=''))),
            free=Count('id', filter=Q(status=False) & (Q(reserved_plate__isnull=True) | Q(reserved_plate='')) & (Q(current_plate__isnull=True) | Q(current_plate=''))),
            reserved=Count('id', filter=Q(status=False) & ~(Q(reserved_plate__isnull=True) | Q(reserved_plate=''))),
            maintenance=Count('id', filter=Q(status=True)),
        )
        total_spots = spot_stats['total'] or 1
        occupancy_rate = round(spot_stats['occupied'] / total_spots * 100, 1)

        # 3. 系统健康度 — 对应 _7 下方 "系统运行状况" 区域
        device_health = Device.objects.aggregate(
            total=Count('id'),
            online=Count('id', filter=Q(status=Device.Status.ONLINE)),
            avg_uptime=Avg('uptime'),
        )

        # 4. 预警模块已下线，返回固定空统计避免前端字段缺失
        alert_stats = {
            'pending': 0,
            'total_today': 0,
        }

        # 5. 今日流量 — 对应 _7 "车辆流量" 区域
        today_traffic = ParkingSession.objects.filter(
            entry_time__date=today
        ).count()

        return Response({
            'daily_revenue': float(daily_revenue),
            'occupancy': {
                **spot_stats,
                'occupancy_rate': occupancy_rate,
            },
            'system_health': device_health,
            'alerts': alert_stats,
            'today_traffic': today_traffic,
        })
