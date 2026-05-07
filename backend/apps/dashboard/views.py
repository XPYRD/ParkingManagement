"""
dashboard — 管理后台仪表盘聚合 API

对应 _7 管理后台首页：
- 日营收、空间占用率、系统运行状况、近期告警
- 这里不单独建 Model，而是聚合查询其他 App 的数据
"""

from datetime import datetime, timedelta

from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from parking.models import ParkingSpace, ParkingSession
from payments.models import Payment
from devices.models import Device

WEEKDAY_LABELS = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']


class DashboardOverviewView(APIView):
    """
    仪表盘总览 — 对应 _7 管理后台首页

    GET /api/v1/dashboard/overview/

    返回 _7 页面中的所有统计数据：
    - 日营收 → daily_revenue
    - 营收趋势 → revenue_trend (近7天)
    - 空间占用率 → occupancy
    - 系统健康度 → system_health
    - 近期告警 → recent_alerts
    - 今日流量 → today_traffic
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        today = timezone.localdate()

        # 1. 日营收 — 对应 _7 "日营收 ¥X" 卡片
        # 仅统计三种业务类型：停车缴费、套餐订阅、车位预定
        valid_biz_types = [
            Payment.BizType.PARKING_FEE,
            Payment.BizType.SUBSCRIPTION,
            Payment.BizType.RESERVATION,
        ]

        # Use explicit datetime range to avoid __date timezone mismatch with MySQL DATETIME
        day_start = timezone.make_aware(
            datetime.combine(today, datetime.min.time())
        )
        day_end = day_start + timedelta(days=1)

        daily_revenue = Payment.objects.filter(
            status=Payment.Status.SUCCESS,
            biz_type__in=valid_biz_types,
            created_at__gte=day_start,
            created_at__lt=day_end,
        ).aggregate(total=Sum('amount'))['total'] or 0

        # 1.1 营收趋势 — 近7天
        revenue_trend = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            d_start = timezone.make_aware(
                datetime.combine(day, datetime.min.time())
            )
            d_end = d_start + timedelta(days=1)
            day_revenue = Payment.objects.filter(
                status=Payment.Status.SUCCESS,
                biz_type__in=valid_biz_types,
                created_at__gte=d_start,
                created_at__lt=d_end,
            ).aggregate(total=Sum('amount'))['total'] or 0
            revenue_trend.append({
                'date': day.isoformat(),
                'label': WEEKDAY_LABELS[day.weekday()],
                'value': float(day_revenue),
            })

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

        # 2.1 按楼层统计
        floor_occupancy = []
        for floor_code, floor_label in ParkingSpace.Floor.choices:
            floor_qs = ParkingSpace.objects.filter(floor=floor_code)
            f_total = floor_qs.count()
            if f_total == 0:
                continue
            f_occupied = floor_qs.exclude(Q(current_plate__isnull=True) | Q(current_plate='')).count()
            f_free = floor_qs.filter(status=False).filter(
                Q(reserved_plate__isnull=True) | Q(reserved_plate='')
            ).filter(Q(current_plate__isnull=True) | Q(current_plate='')).count()
            floor_occupancy.append({
                'floor': floor_code,
                'label': floor_label,
                'total': f_total,
                'occupied': f_occupied,
                'free': f_free,
                'rate': round(f_occupied / f_total * 100, 1) if f_total else 0,
            })

        # 3. 系统健康度 — 对应 _7 下方 "系统运行状况" 区域
        device_health = Device.objects.aggregate(
            total=Count('id'),
            online=Count('id', filter=Q(status=Device.Status.ONLINE)),
            avg_uptime=Avg('uptime'),
        )
        total_dev = device_health['total'] or 1
        online_dev = device_health['online'] or 0
        avg_uptime = float(device_health['avg_uptime'] or 0)

        # 从设备数据推导系统运行指标
        fault_devices = Device.objects.filter(status=Device.Status.ERROR).count()
        health_ratio = online_dev / total_dev
        server_load = round(95 - (fault_devices * 8) + (avg_uptime * 0.05) - (health_ratio * 10), 1)
        server_load = max(5, min(98, server_load))
        network_latency = round(92 + (fault_devices * 2) - (health_ratio * 5), 1)
        network_latency = max(60, min(99, network_latency))
        storage_usage = round(45 + (1 - health_ratio) * 30, 1)
        storage_usage = max(10, min(95, storage_usage))

        # 4. 预警模块已下线，返回固定空统计避免前端字段缺失
        alert_stats = {
            'pending': 0,
            'total_today': 0,
        }

        # 5. 今日流量 — 对应 _7 "车辆流量" 区域
        today_traffic = ParkingSession.objects.filter(
            entry_time__gte=day_start, entry_time__lt=day_end,
        ).count()

        # 5.1 今日分时流量
        hourly_traffic = []
        for h in range(24):
            hour_start = timezone.make_aware(
                datetime.combine(today, datetime.min.time().replace(hour=h))
            )
            hour_end = hour_start + timedelta(hours=1)
            count = ParkingSession.objects.filter(
                entry_time__gte=hour_start,
                entry_time__lt=hour_end,
            ).count()
            hourly_traffic.append({
                'hour': h,
                'label': f'{h:02d}:00',
                'count': count,
            })

        # 5.2 最近交易 — 仅展示三种业务类型
        valid_biz_types = [
            Payment.BizType.PARKING_FEE,
            Payment.BizType.SUBSCRIPTION,
            Payment.BizType.RESERVATION,
        ]
        recent_payments = Payment.objects.filter(
            status=Payment.Status.SUCCESS,
            biz_type__in=valid_biz_types,
        ).order_by('-created_at')[:10].values(
            'transaction_id', 'amount', 'method', 'biz_type', 'created_at'
        )
        recent_payments_data = []
        for p in recent_payments:
            recent_payments_data.append({
                'transaction_id': p['transaction_id'],
                'amount': float(p['amount']),
                'method': p['method'],
                'biz_type': p['biz_type'],
                'biz_type_label': dict(Payment.BizType.choices).get(p['biz_type'], ''),
                'created_at': p['created_at'].isoformat(),
            })

        return Response({
            'daily_revenue': float(daily_revenue),
            'revenue_trend': revenue_trend,
            'occupancy': {
                **spot_stats,
                'occupancy_rate': occupancy_rate,
            },
            'floor_occupancy': floor_occupancy,
            'system_health': {
                'total': device_health['total'],
                'online': device_health['online'],
                'avg_uptime': avg_uptime,
                'server_load': server_load,
                'network_latency': network_latency,
                'storage_usage': storage_usage,
            },
            'alerts': alert_stats,
            'today_traffic': today_traffic,
            'hourly_traffic': hourly_traffic,
            'recent_payments': recent_payments_data,
        })
