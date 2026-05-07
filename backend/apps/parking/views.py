"""
parking — API 视图

端点清单：
- GET    /api/v1/parking/spots/                   车位列表（地图/管理端）
- GET    /api/v1/parking/spots/{id}/              车位详情
- POST   /api/v1/parking/spots/                   [管理端] 创建车位
- PUT    /api/v1/parking/spots/{id}/              [管理端] 更新车位
- GET    /api/v1/parking/spots/floor-summary/     按楼层统计占用率
- GET    /api/v1/parking/sessions/                停车会话列表
- GET    /api/v1/parking/sessions/current/        当前活跃会话
- POST   /api/v1/parking/sessions/                [管理端] 创建会话（入场）
- PATCH  /api/v1/parking/sessions/{id}/           [管理端] 更新会话（出场）
- GET    /api/v1/parking/reservations/            我的预约列表
- POST   /api/v1/parking/reservations/            创建预约
- PATCH  /api/v1/parking/reservations/{id}/cancel/ 取消预约

新增（室内地图与反向寻车模块）：
- GET    /api/v1/map/spaces/                      全量车位状态（地图初始化）
- GET    /api/v1/map/find_car/                    根据车牌号寻车
- POST   /api/v1/hardware/webhook/                硬件推送的车位变化事件
"""

import time
from pathlib import Path
import re
import logging

from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import permission_classes
from rest_framework.decorators import action, api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

logger = logging.getLogger(__name__)

from .models import ParkingSession, Reservation, SpotConnection, ParkingSpace
from payments.models import PricingRule, Subscription
from .serializers import (
    ParkingSpotSerializer,
    ParkingSessionSerializer,
    ReservationSerializer,
    SpotConnectionSerializer,
    NavigationPathSerializer,
    ParkingSpaceSerializer,
    MapSpacesResponseSerializer,
    FindCarResponseSerializer,
    NavigationStartPointSerializer,
)
from .navigation import find_path

def _spot_xy(spot):
    """Return (x, y) for a spot, preferring center coordinates."""
    x = spot.center_x if spot.center_x is not None else (spot.x or 0)
    y = spot.center_y if spot.center_y is not None else (spot.y or 0)
    return float(x), float(y)


def _display_name(spot):
    if spot.node_type == ParkingSpace.NodeType.LOCATION:
        return spot.location_name or spot.space_id
    return spot.space_id


def _compute_direct_path(start_spot, end_spot):
    """
    计算起点到终点的直接路径（图不可达时的回退方案）。

    规则：
    - 同楼层：直接连线
    - 跨楼层：在中间楼层插入转折点（电梯/楼梯模拟）
    """
    import math
    sx, sy = _spot_xy(start_spot)
    ex, ey = _spot_xy(end_spot)

    dist = math.sqrt((sx - ex) ** 2 + (sy - ey) ** 2)

    if start_spot.floor == end_spot.floor:
        # 同楼层 — 直接连线
        return {
            'path': [_display_name(start_spot), _display_name(end_spot)],
            'path_node_ids': [start_spot.space_id, end_spot.space_id],
            'path_points': [{'x': sx, 'y': sy}, {'x': ex, 'y': ey}],
            'distance': round(dist, 2),
            'steps': [{
                'from_id': start_spot.space_id,
                'to_id': end_spot.space_id,
                'from': _display_name(start_spot),
                'to': _display_name(end_spot),
                'distance': round(dist, 2),
                'from_coords': {'x': sx, 'y': sy},
                'to_coords': {'x': ex, 'y': ey},
            }],
        }

    # 跨楼层 — 插入中间转折点
    floor_order = ['B2', 'B1', '1F']
    try:
        si = floor_order.index(start_spot.floor)
        ei = floor_order.index(end_spot.floor)
    except ValueError:
        si, ei = 0, len(floor_order) - 1

    min_idx, max_idx = min(si, ei), max(si, ei)
    intermediate_floors = floor_order[min_idx + 1:max_idx]

    path_spots = [_display_name(start_spot)]
    path_node_ids = [start_spot.space_id]
    path_points = [{'x': sx, 'y': sy}]
    steps = []

    prev_x, prev_y = sx, sy
    prev_spot = start_spot

    for floor in intermediate_floors:
        # 使用水平中点作为电梯位置
        mid_x = (sx + ex) / 2
        mid_y = (sy + ey) / 2
        path_spots.append(f'{floor}-电梯')
        path_node_ids.append(f'elevator_{floor}')
        path_points.append({'x': mid_x, 'y': mid_y})
        step_dist = math.sqrt((prev_x - mid_x) ** 2 + (prev_y - mid_y) ** 2)
        steps.append({
            'from_id': prev_spot.space_id,
            'to_id': f'elevator_{floor}',
            'from': _display_name(prev_spot),
            'to': f'{floor}-电梯',
            'distance': round(step_dist, 2),
            'from_coords': {'x': prev_x, 'y': prev_y},
            'to_coords': {'x': mid_x, 'y': mid_y},
        })
        prev_x, prev_y = mid_x, mid_y
        prev_spot = end_spot  # simplified

    # 最后一段到终点
    final_dist = math.sqrt((prev_x - ex) ** 2 + (prev_y - ey) ** 2)
    path_spots.append(_display_name(end_spot))
    path_node_ids.append(end_spot.space_id)
    path_points.append({'x': ex, 'y': ey})
    steps.append({
        'from_id': prev_spot.space_id if prev_spot != end_spot else start_spot.space_id,
        'to_id': end_spot.space_id,
        'from': _display_name(start_spot) if prev_spot == end_spot else _display_name(prev_spot),
        'to': _display_name(end_spot),
        'distance': round(final_dist, 2),
        'from_coords': {'x': prev_x, 'y': prev_y},
        'to_coords': {'x': ex, 'y': ey},
    })

    return {
        'path': path_spots,
        'path_node_ids': path_node_ids,
        'path_points': path_points,
        'distance': round(dist, 2),
        'steps': steps,
    }


_PLATE_OCR_ENGINE = None
_PLATE_REGEXES = [
    re.compile(r'[\u4e00-\u9fa5][A-Z][A-Z0-9]{5}'),
    re.compile(r'[\u4e00-\u9fa5][A-Z][A-Z0-9]{6}'),
]


def _normalize_plate_text(value):
    return str(value or '').upper().replace('·', '').replace('.', '').replace(' ', '').strip()


def _extract_plate_from_texts(texts):
    for raw in texts:
        text = _normalize_plate_text(raw)
        if not text:
            continue
        for pattern in _PLATE_REGEXES:
            match = pattern.search(text)
            if match:
                return match.group(0)
    return ''


def _get_plate_ocr_engine():
    global _PLATE_OCR_ENGINE
    if _PLATE_OCR_ENGINE is not None:
        return _PLATE_OCR_ENGINE
    try:
        from paddleocr import PaddleOCR  # type: ignore
        logger.info('初始化 PaddleOCR 引擎...')
        _PLATE_OCR_ENGINE = PaddleOCR(use_angle_cls=True, lang='ch')
        logger.info('✓ PaddleOCR 引擎初始化成功')
    except ImportError as e:
        logger.error(f'✗ PaddleOCR 模块未安装或导入失败: {e}')
        _PLATE_OCR_ENGINE = False
    except Exception as e:
        logger.error(f'✗ PaddleOCR 初始化失败: {e}', exc_info=True)
        _PLATE_OCR_ENGINE = False
    return _PLATE_OCR_ENGINE


def _infer_energy_type(plate):
    """
    根据车牌号推断车辆类型
    新能源车牌：6位字符（如 粤AD12345），燃油车：5位字符（如 粤A12345）
    """
    if not plate:
        return 'unknown'
    # 去掉首位的汉字和字母（省份代码），看剩余位数
    rest = plate[2:] if len(plate) > 2 else ''
    if len(rest) >= 6:
        return 'new_energy'
    return 'ICE'


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@parser_classes([MultiPartParser, FormParser])
def ai_recognize_plate(request):
    """AI 车牌识别接口：供首页进场模拟上传图片识别使用。"""
    image_file = request.FILES.get('image')
    if not image_file:
        logger.warning('请求缺少 image 文件')
        return Response({'detail': '缺少 image 文件'}, status=status.HTTP_400_BAD_REQUEST)

    logger.info(f'开始识别图片: {image_file.name} (大小: {image_file.size} bytes)')

    # 兜底方案：先尝试从文件名中提取车牌
    filename_plate = _extract_plate_from_texts([getattr(image_file, 'name', '')])
    if filename_plate:
        logger.info(f'✓ 从文件名提取到车牌: {filename_plate}')

    # 主方案：使用 OCR 识别
    ocr_plate = ''
    ocr_engine = _get_plate_ocr_engine()

    if not ocr_engine:
        logger.warning('✗ OCR 引擎未初始化或初始化失败，跳过 OCR 识别，使用文件名兜底')
    else:
        try:
            import numpy as np  # type: ignore
            import cv2  # type: ignore

            logger.debug('开始读取和解析图片...')
            file_bytes = np.asarray(bytearray(image_file.read()), dtype=np.uint8)
            image_file.seek(0)

            logger.debug(f'图片字节数: {len(file_bytes)}')
            image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

            if image is None:
                logger.error('✗ cv2.imdecode 返回 None，图片格式可能不支持或数据损坏')
            else:
                logger.debug(f'✓ 图片成功解析，尺寸: {image.shape}')
                logger.debug('调用 PaddleOCR 进行识别...')
                result = ocr_engine.ocr(image, cls=True)

                logger.debug(f'OCR 原始结果类型: {type(result)}, 长度: {len(result) if result else 0}')

                texts = []
                if result:
                    for block in result:
                        for line in block or []:
                            if isinstance(line, (list, tuple)) and len(line) >= 2:
                                rec = line[1]
                                if isinstance(rec, (list, tuple)) and rec:
                                    text = rec[0]
                                    conf = rec[1] if len(rec) > 1 else 0
                                    logger.debug(f'    文本="{text}", 置信度={conf:.2f}')
                                    texts.append(text)

                logger.debug(f'提取文本: {texts}')
                ocr_plate = _extract_plate_from_texts(texts)
                if ocr_plate:
                    logger.info(f'✓ OCR 识别到车牌: {ocr_plate}')
                else:
                    logger.warning('✗ OCR 识别成功但未提取到有效车牌')

        except ImportError as e:
            logger.error(f'✗ 缺少依赖库 (numpy/cv2): {e}')
        except Exception as e:
            logger.error(f'✗ OCR 识别过程异常: {e}', exc_info=True)
            ocr_plate = ''

    plate_number = ocr_plate or filename_plate
    if not plate_number:
        logger.warning('识别失败：既未从 OCR 提取，也未从文件名提取到车牌')
        return Response({
            'success': False,
            'detail': '未识别到车牌，请重试或手动输入',
            'plate_number': '',
            'energy_type': 'unknown',
        }, status=status.HTTP_200_OK)

    energy_type = _infer_energy_type(plate_number)
    logger.info(f'✓ 最终识别结果: {plate_number} (来源: {"ocr" if ocr_plate else "filename"}, 类型: {energy_type})')
    return Response({
        'success': True,
        'plate_number': plate_number,
        'energy_type': energy_type,
        'source': 'ocr' if ocr_plate else 'filename',
    }, status=status.HTTP_200_OK)


class ParkingSpotViewSet(viewsets.ModelViewSet):
    """
    车位管理 — 对应 _2 智能地图 + _8 车位管理后台

    用户端（地图）：只读，按楼层/区域筛选
    管理端：完整 CRUD

    地图场景需要一次获取某楼层全部车位，因此支持 ?no_page=1 取消分页。
    """
    serializer_class = ParkingSpotSerializer
    queryset = ParkingSpace.objects.all()
    filterset_fields = ['floor']
    search_fields = ['space_id', 'current_plate']
    ordering_fields = ['spot_id', 'floor', 'status']

    @property
    def pagination_class(self):
        """地图场景传入 no_page=1 时取消分页，返回全量数据"""
        if self.request.query_params.get('no_page'):
            return None
        return super().pagination_class

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        status_param = self.request.query_params.get('status', '').strip()
        type_param = self.request.query_params.get('type', '').strip()

        if status_param:
            if status_param == 'free':
                queryset = queryset.filter(
                    status=False,
                    current_plate__isnull=True,
                ).filter(Q(reserved_plate__isnull=True) | Q(reserved_plate=''))
            elif status_param == 'occupied':
                queryset = queryset.filter(status=False).exclude(
                    Q(current_plate__isnull=True) | Q(current_plate='')
                )
            elif status_param == 'reserved':
                queryset = queryset.filter(
                    status=False,
                    reserved_plate__isnull=False,
                ).exclude(reserved_plate='').filter(
                    Q(current_plate__isnull=True) | Q(current_plate='')
                )
            elif status_param == 'maintenance':
                queryset = queryset.filter(status=True)

        if type_param:
            if type_param == 'ev':
                queryset = queryset.filter(type=True)
            elif type_param == 'standard':
                queryset = queryset.filter(type=False)

        return queryset

    def get_permissions(self):
        """用户端只允许查看，管理端允许增删改"""
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


    @action(detail=True, methods=['post'], url_path='toggle-maintenance')
    def toggle_maintenance(self, request, pk=None):
        """
        切换车位维护状态 — 对应 _8 修停/恢复按钮

        POST /api/v1/parking/spots/{id}/toggle-maintenance/
        { "maintenance": true }   → 设为维护中
        { "maintenance": false }  → 恢复正常
        """
        spot = self.get_object()
        maintenance = request.data.get('maintenance')
        if maintenance is None:
            return Response({'detail': '缺少 maintenance 字段'}, status=400)

        spot.status = bool(maintenance)
        spot.save(update_fields=['status'])
        serializer = self.get_serializer(spot)
        return Response(serializer.data)


    @action(detail=False, methods=['get'], url_path='floor-summary')
    @permission_classes([permissions.AllowAny])
    def floor_summary(self, request):
        """
        按楼层统计车位占用率 — 对应 _2 侧边栏 "空间占用率 84%"

        GET /api/v1/parking/spots/floor-summary/
        返回：[{floor, total, free, occupied, occupancy_rate}, ...]
        """
        result = []
        floors = ParkingSpace.objects.values_list('floor', flat=True).distinct().order_by('floor')
        for floor in floors:
            floor_qs = ParkingSpace.objects.filter(floor=floor)
            total = floor_qs.count()
            occupied = floor_qs.exclude(Q(current_plate__isnull=True) | Q(current_plate='')).count()
            maintenance = floor_qs.filter(status=True).count()
            free = floor_qs.filter(status=False).filter(
                Q(reserved_plate__isnull=True) | Q(reserved_plate='')
            ).filter(Q(current_plate__isnull=True) | Q(current_plate='')).count()
            rate = round(occupied / total * 100, 1) if total > 0 else 0
            result.append({
                'floor': floor,
                'total': total,
                'free': free,
                'occupied': occupied,
                'maintenance': maintenance,
                'occupancy_rate': rate,
            })
        return Response(result)


class ParkingSessionViewSet(viewsets.ModelViewSet):
    """
    停车会话 — 对应 _4 当前停车卡片

    用户端：查看自己车辆的会话
    管理端：查看所有会话
    """
    serializer_class = ParkingSessionSerializer
    filterset_fields = ['payment_status']
    search_fields = ['vehicle__plate_number']
    ordering_fields = ['entry_time', 'amount']

    def get_permissions(self):
        if self.action in ('by_plate', 'quick_pay', 'mark_exit'):
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return ParkingSession.objects.all()
        if user.is_staff:
            return ParkingSession.objects.all()
        return ParkingSession.objects.filter(vehicle__owner=user)

    @action(detail=False, methods=['get'], url_path='current')
    def current(self, request):
        """
        当前活跃停车会话 — 对应 _4 页面顶部 "当前停车" 卡片

        GET /api/v1/parking/sessions/current/
        返回当前用户仍在场内的会话（exit_time 为空）
        """
        sessions = self.get_queryset().filter(exit_time__isnull=True)
        today = timezone.localdate()
        has_active_sub = Subscription.objects.filter(
            user=request.user,
            is_active=True,
            start_date__lte=today,
            end_date__gte=today,
        ).exists()

        if has_active_sub:
            sessions.exclude(
                amount=0,
                payment_status=ParkingSession.PaymentStatus.PAID,
            ).update(
                amount=0,
                payment_status=ParkingSession.PaymentStatus.PAID,
            )

            sessions = self.get_queryset().filter(exit_time__isnull=True)
        serializer = self.get_serializer(sessions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-plate')
    @permission_classes([permissions.AllowAny])
    def by_plate(self, request):
        """根据车牌号查询当前在场停车费用（首页快速缴费·无需登录查询）。"""
        plate = request.query_params.get('plate', '').strip().upper()
        if not plate:
            return Response({'detail': '缺少 plate 参数'}, status=status.HTTP_400_BAD_REQUEST)

        from accounts.models import Vehicle, User
        from decimal import Decimal
        from payments.models import PricingRule, Subscription

        # 1. 优先从 ParkingSession 查找（已注册车辆）
        vehicle = Vehicle.objects.filter(plate_number__iexact=plate).first()
        session = None

        if vehicle:
            session = ParkingSession.objects.filter(
                vehicle=vehicle, exit_time__isnull=True
            ).first()

        # 2. 兜底：从车位 current_plate 查找（未注册车辆/模拟进场）
        entry_time = None
        if not session:
            space_with_plate = ParkingSpace.objects.filter(
                current_plate__iexact=plate
            ).exclude(current_plate__isnull=True).exclude(current_plate='').first()

            if space_with_plate:
                entry_time = space_with_plate.bind_time or space_with_plate.last_updated or timezone.now()
                if vehicle:
                    session = ParkingSession.objects.create(
                        vehicle=vehicle,
                        spot=space_with_plate,
                        entry_time=entry_time,
                        amount=Decimal('0'),
                        payment_status=ParkingSession.PaymentStatus.PENDING,
                    )

        if not session and not entry_time:
            return Response({
                'found': False,
                'detail': '未找到该车牌在场停车记录',
            })

        # 3. 订阅检查：如果该车牌是某订阅用户的绑定车辆 → 免费
        has_active_sub = False
        today = timezone.localdate()
        if vehicle:
            has_active_sub = Subscription.objects.filter(
                user=vehicle.owner,
                is_active=True,
                start_date__lte=today,
                end_date__gte=today,
            ).exists()

        # 有订阅则自动标记免费
        if session and has_active_sub and session.payment_status != ParkingSession.PaymentStatus.PAID:
            session.amount = 0
            session.payment_status = ParkingSession.PaymentStatus.PAID
            session.save(update_fields=['amount', 'payment_status'])

        # 4. 计算停车时长和费用
        effective_entry = session.entry_time if session else entry_time
        now = timezone.now()
        duration = now - effective_entry
        total_minutes = int(duration.total_seconds() / 60)
        hours = total_minutes // 60
        mins = total_minutes % 60
        chargeable_hours = max(1, hours + (1 if mins > 0 else 0))

        if has_active_sub:
            amount = Decimal('0')
        else:
            hourly_rate = PricingRule.get_active_value(
                PricingRule.RateType.HOURLY_STANDARD, Decimal('6.00')
            ) or Decimal('6.00')
            amount = hourly_rate * chargeable_hours

        # 5. 检查待出场状态（缴费后30分钟内）
        payment_state = session.payment_status if session else ParkingSession.PaymentStatus.PENDING
        if session and session.payment_status == ParkingSession.PaymentStatus.PAID:
            payment_state = ParkingSession.PaymentStatus.PAID
        elif not session and space_with_plate and space_with_plate.pending_exit_plate:
            from django.utils.dateparse import parse_datetime
            pending_time = space_with_plate.pending_exit_time
            if pending_time:
                if timezone.is_naive(pending_time):
                    pending_time = timezone.make_aware(pending_time)
                elapsed = (timezone.now() - pending_time).total_seconds()
                if elapsed <= 1800:  # 30分钟内
                    payment_state = 'pending_exit'

        return Response({
            'session_id': session.id if session else None,
            'plate_number': vehicle.plate_number if vehicle else plate,
            'entry_time': effective_entry.isoformat(),
            'duration_text': f'{hours}小时{mins}分钟',
            'chargeable_hours': chargeable_hours,
            'amount': float(amount),
            'payment_state': payment_state,
            'found': True,
            'subscription_free': has_active_sub,
        })

    @action(detail=False, methods=['post'], url_path='quick-pay-by-plate')
    @permission_classes([permissions.AllowAny])
    def quick_pay_by_plate(self, request):
        """通过车牌号直接缴费（无 session_id 的场景，如从车位记录查询的车辆）。"""
        from accounts.models import User, Vehicle
        from decimal import Decimal, InvalidOperation
        from payments.models import Payment, Subscription

        plate = request.data.get('plate_number', '').strip().upper()
        if not plate:
            return Response({'detail': '缺少 plate_number 参数'}, status=status.HTTP_400_BAD_REQUEST)

        amount = request.data.get('amount')
        method = request.data.get('method', 'wechat')

        # 订阅检查
        today = timezone.localdate()
        has_active_sub = Subscription.objects.filter(
            user__vehicles__plate_number__iexact=plate,
            is_active=True,
            start_date__lte=today,
            end_date__gte=today,
        ).exists()

        if has_active_sub:
            return Response({
                'payment_state': 'subscription_free',
                'leave_tip': '当前订阅有效，车辆进出场免费，无需支付',
                'session_id': None,
            })

        try:
            amount_dec = Decimal(str(amount))
        except (InvalidOperation, TypeError, ValueError):
            return Response({'detail': '金额格式错误'}, status=status.HTTP_400_BAD_REQUEST)

        # 余额支付：需要登录，直接扣款并标记已缴费
        if method == 'balance':
            if not request.user.is_authenticated:
                return Response({'detail': '余额支付需要先登录'}, status=status.HTTP_401_UNAUTHORIZED)
            try:
                balance_obj = request.user.balance
            except Exception:
                return Response({'detail': '账户余额不存在'}, status=status.HTTP_400_BAD_REQUEST)
            if balance_obj.balance < amount_dec:
                return Response({'detail': '余额不足'}, status=status.HTTP_400_BAD_REQUEST)

            transaction_id = f"QUICK_{int(time.time() * 1000)}"
            vehicle = Vehicle.objects.filter(plate_number__iexact=plate).first()
            space_with_plate = ParkingSpace.objects.filter(
                current_plate__iexact=plate
            ).exclude(current_plate__isnull=True).exclude(current_plate='').first()

            # 设置待出场状态
            if space_with_plate:
                space_with_plate.pending_exit_plate = plate
                space_with_plate.pending_exit_time = timezone.now()
                space_with_plate.save(update_fields=['pending_exit_plate', 'pending_exit_time'])

            # 创建/更新 ParkingSession（vehicle 必须存在，因为该字段不允许 NULL）
            session = None
            if vehicle:
                session = ParkingSession.objects.filter(
                    vehicle=vehicle, exit_time__isnull=True
                ).first()
                if not session and space_with_plate:
                    entry_time = space_with_plate.bind_time or space_with_plate.last_updated or timezone.now()
                    session = ParkingSession.objects.create(
                        vehicle=vehicle,
                        spot=space_with_plate,
                        entry_time=entry_time,
                        amount=amount_dec,
                        payment_status=ParkingSession.PaymentStatus.PAID,
                    )
                if session and session.payment_status != ParkingSession.PaymentStatus.PAID:
                    session.payment_status = ParkingSession.PaymentStatus.PAID
                    session.amount = amount_dec
                    session.save(update_fields=['payment_status', 'amount'])
            if session and session.payment_status != ParkingSession.PaymentStatus.PAID:
                session.payment_status = ParkingSession.PaymentStatus.PAID
                session.amount = amount_dec
                session.save(update_fields=['payment_status', 'amount'])

            Payment.objects.create(
                user=request.user,
                transaction_id=transaction_id,
                amount=amount_dec,
                method=Payment.Method.BALANCE,
                status=Payment.Status.SUCCESS,
                biz_type=Payment.BizType.PARKING_FEE,
                remark=f'快速缴费（余额）{plate}',
                session_id=session.id if session else None,
            )
            balance_obj.balance -= amount_dec
            balance_obj.total_consumed += amount_dec
            balance_obj.save()

            return Response({
                'payment_state': 'paid',
                'transaction_id': transaction_id,
                'amount': f"{amount_dec:.2f}",
                'plate_number': plate,
                'session_id': session.id if session else None,
            }, status=status.HTTP_201_CREATED)

        transaction_id = f"QUICK_{int(time.time() * 1000)}"
        vehicle = Vehicle.objects.filter(plate_number__iexact=plate).first()
        if request.user.is_authenticated:
            payment_user = request.user
        elif vehicle:
            payment_user = vehicle.owner
        else:
            payment_user = User.objects.filter(is_superuser=True).first()

        space_with_plate = ParkingSpace.objects.filter(
            current_plate__iexact=plate
        ).exclude(current_plate__isnull=True).exclude(current_plate='').first()
        entry_time = None
        if not vehicle and space_with_plate:
            entry_time = space_with_plate.bind_time or space_with_plate.last_updated or timezone.now()

        session = None
        if vehicle:
            session = ParkingSession.objects.filter(
                vehicle=vehicle, exit_time__isnull=True
            ).first()
            if not session:
                session = ParkingSession.objects.create(
                    vehicle=vehicle,
                    spot=space_with_plate,
                    entry_time=entry_time or timezone.now(),
                    amount=amount_dec,
                    payment_status=ParkingSession.PaymentStatus.PENDING,
                )
        elif space_with_plate and vehicle:
            # 已注册车辆但无会话：创建会话
            session = ParkingSession.objects.create(
                vehicle=vehicle,
                spot=space_with_plate,
                entry_time=entry_time or timezone.now(),
                amount=amount_dec,
                payment_status=ParkingSession.PaymentStatus.PENDING,
            )

        # 未注册车辆时，用 superuser 作为 Payment 的归属用户
        if not payment_user:
            payment_user = User.objects.filter(is_superuser=True).first()

        payment = Payment.objects.create(
            user=payment_user,
            transaction_id=transaction_id,
            amount=amount_dec,
            method=method,
            status=Payment.Status.PENDING,
            biz_type=Payment.BizType.PARKING_FEE,
            remark=f'快速缴费（按车牌）{plate}',
            session_id=session.id if session else None,
        )

        from urllib.parse import quote_plus
        payload = f"SANDBOX|quick_pay|{transaction_id}|{amount}|{method}"
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=260x260&data={quote_plus(payload)}"

        return Response({
            'payment_state': 'pending',
            'transaction_id': transaction_id,
            'amount': f"{amount_dec:.2f}",
            'plate_number': plate,
            'qr_code_url': qr_url,
            'session_id': session.id if session else None,
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='quick-pay')
    @permission_classes([permissions.AllowAny])
    def quick_pay(self, request, pk=None):
        """快速缴费（无需登录）：检查订阅 → 创建支付 → 返回二维码。"""
        session = self.get_object()
        if session.exit_time:
            return Response({'detail': '车辆已出场'}, status=status.HTTP_400_BAD_REQUEST)
        if session.payment_status == ParkingSession.PaymentStatus.PAID:
            return Response({'detail': '该会话已支付'}, status=status.HTTP_400_BAD_REQUEST)

        amount = request.data.get('amount')
        method = request.data.get('method', 'wechat')
        plate = request.data.get('plate_number', '').strip().upper()

        # 检查车主是否有有效订阅
        from payments.models import Subscription
        today = timezone.localdate()
        has_active_sub = Subscription.objects.filter(
            user__vehicles__plate_number__iexact=plate,
            is_active=True,
            start_date__lte=today,
            end_date__gte=today,
        ).exists()

        if has_active_sub:
            session.amount = 0
            session.payment_status = ParkingSession.PaymentStatus.PAID
            session.save(update_fields=['amount', 'payment_status'])
            return Response({
                'payment_state': 'subscription_free',
                'leave_tip': '当前订阅有效，车辆进出场免费，无需支付',
                'session_id': session.id,
            })

        # 无订阅：创建待支付订单
        from decimal import Decimal, InvalidOperation
        try:
            amount_dec = Decimal(str(amount))
        except (InvalidOperation, TypeError, ValueError):
            return Response({'detail': '金额格式错误'}, status=status.HTTP_400_BAD_REQUEST)

        from payments.models import Payment

        # 余额支付：需要登录，直接扣款并标记已缴费
        if method == 'balance':
            if not request.user.is_authenticated:
                return Response({'detail': '余额支付需要先登录'}, status=status.HTTP_401_UNAUTHORIZED)
            try:
                balance_obj = request.user.balance
            except Exception:
                return Response({'detail': '账户余额不存在'}, status=status.HTTP_400_BAD_REQUEST)
            if balance_obj.balance < amount_dec:
                return Response({'detail': '余额不足'}, status=status.HTTP_400_BAD_REQUEST)

            transaction_id = f"QUICK_{int(time.time() * 1000)}"

            # 设置待出场状态
            if session.spot:
                session.spot.pending_exit_plate = plate
                session.spot.pending_exit_time = timezone.now()
                session.spot.save(update_fields=['pending_exit_plate', 'pending_exit_time'])

            session.payment_status = ParkingSession.PaymentStatus.PAID
            session.amount = amount_dec
            session.save(update_fields=['payment_status', 'amount'])

            Payment.objects.create(
                user=request.user,
                transaction_id=transaction_id,
                amount=amount_dec,
                method=Payment.Method.BALANCE,
                status=Payment.Status.SUCCESS,
                biz_type=Payment.BizType.PARKING_FEE,
                remark=f'快速缴费（余额）{plate}',
                session_id=session.id,
            )
            balance_obj.balance -= amount_dec
            balance_obj.total_consumed += amount_dec
            balance_obj.save()

            return Response({
                'payment_state': 'paid',
                'transaction_id': transaction_id,
                'amount': f"{amount_dec:.2f}",
                'plate_number': plate,
                'session_id': session.id,
            }, status=status.HTTP_201_CREATED)

        transaction_id = f"QUICK_{int(time.time() * 1000)}"
        if request.user.is_authenticated:
            payment_user = request.user
        elif session.vehicle:
            payment_user = session.vehicle.owner
        else:
            payment_user = None
        if not payment_user:
            payment_user = User.objects.filter(is_superuser=True).first()
        payment = Payment.objects.create(
            user=payment_user,
            transaction_id=transaction_id,
            amount=amount_dec,
            method=method,
            status=Payment.Status.PENDING,
            biz_type=Payment.BizType.PARKING_FEE,
            remark=f'快速缴费 {plate}',
            session_id=session.id,
        )

        from urllib.parse import quote_plus
        payload = f"SANDBOX|quick_pay|{transaction_id}|{amount}|{method}"
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=260x260&data={quote_plus(payload)}"

        return Response({
            'payment_state': 'pending',
            'transaction_id': transaction_id,
            'amount': f"{amount_dec:.2f}",
            'plate_number': plate,
            'qr_code_url': qr_url,
            'session_id': session.id,
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='confirm-quick-pay')
    @permission_classes([permissions.AllowAny])
    def confirm_quick_pay(self, request):
        """确认快速缴费完成（模拟支付成功），设置车位为待出场状态，并写入 ParkingSession 持久化。"""
        from accounts.models import User, Vehicle

        session_id = request.data.get('session_id')
        plate = request.data.get('plate_number', '').strip().upper()

        if not plate:
            return Response({'detail': '缺少 plate_number 参数'}, status=status.HTTP_400_BAD_REQUEST)

        # 查找车位
        spot = ParkingSpace.objects.filter(
            current_plate__iexact=plate
        ).exclude(current_plate__isnull=True).exclude(current_plate='').first()

        if not spot:
            return Response({'detail': '未找到该车位'}, status=status.HTTP_404_NOT_FOUND)

        # 设置待出场状态
        spot.pending_exit_plate = plate
        spot.pending_exit_time = timezone.now()
        spot.save(update_fields=['pending_exit_plate', 'pending_exit_time'])

        # 确保有 ParkingSession 来持久化已支付状态
        session = None
        vehicle = Vehicle.objects.filter(plate_number__iexact=plate).first()
        if session_id:
            session = ParkingSession.objects.filter(id=session_id).first()

        if not session:
            session = ParkingSession.objects.filter(
                vehicle=vehicle if vehicle else None,
                spot=spot,
                exit_time__isnull=True,
            ).first()

        if not session:
            entry_time = spot.bind_time or spot.last_updated or timezone.now()
            if vehicle:
                session = ParkingSession.objects.create(
                    vehicle=vehicle,
                    spot=spot,
                    entry_time=entry_time,
                    amount=spot.current_plate and Decimal('0') or Decimal('0'),
                    payment_status=ParkingSession.PaymentStatus.PAID,
                )

        if session and session.payment_status != ParkingSession.PaymentStatus.PAID:
            session.payment_status = ParkingSession.PaymentStatus.PAID
            session.save(update_fields=['payment_status'])

        # 同步更新 Payment 记录状态为成功
        from payments.models import Payment
        if session:
            Payment.objects.filter(session_id=session.id).update(status=Payment.Status.SUCCESS)
        else:
            # 未注册车辆：更新最近创建的 PENDING 支付记录
            pay_user = request.user if request.user.is_authenticated else (
                vehicle.owner if vehicle else None
            )
            if not pay_user:
                pay_user = User.objects.filter(is_superuser=True).first()
            if pay_user:
                last_payment = Payment.objects.filter(
                    user=pay_user,
                    status=Payment.Status.PENDING,
                    method__in=['wechat', 'alipay', 'card'],
                ).order_by('-id').first()
                if last_payment:
                    last_payment.status = Payment.Status.SUCCESS
                    last_payment.save(update_fields=['status'])

        return Response({
            'detail': '缴费成功，请在30分钟内离场，超时需重新缴费',
            'pending_exit_time': spot.pending_exit_time.isoformat(),
        })

    @action(detail=True, methods=['post'], url_path='mark-exit')
    @permission_classes([permissions.AllowAny])
    def mark_exit(self, request, pk=None):
        """标记车辆出场（首页模拟出场）。只有订阅用户的绑定车辆可免费出场，其他车辆需先缴费。"""
        session = self.get_object()
        if session.exit_time:
            return Response({'detail': '车辆已出场', 'exit_time': session.exit_time.isoformat()})

        # 判断车主是否有有效订阅
        vehicle = session.vehicle
        today = timezone.localdate()
        has_active_sub = Subscription.objects.filter(
            user=vehicle.owner,
            is_active=True,
            start_date__lte=today,
            end_date__gte=today,
        ).exists()

        if has_active_sub:
            # 订阅用户免费出场
            session.amount = 0
            session.payment_status = ParkingSession.PaymentStatus.PAID
            session.save(update_fields=['amount', 'payment_status'])
        elif session.payment_status != ParkingSession.PaymentStatus.PAID:
            # 非订阅用户检查是否已缴费且在30分钟内
            spot = session.spot
            if spot and spot.pending_exit_plate and spot.pending_exit_time:
                elapsed = (timezone.now() - spot.pending_exit_time).total_seconds()
                if elapsed <= 1800:  # 30分钟内
                    # 已缴费且在有效期内，允许出场
                    session.payment_status = ParkingSession.PaymentStatus.PAID
                    session.save(update_fields=['payment_status'])
                else:
                    # 超过30分钟，清除待出场状态
                    spot.pending_exit_plate = None
                    spot.pending_exit_time = None
                    spot.save(update_fields=['pending_exit_plate', 'pending_exit_time'])
                    return Response(
                        {'detail': '缴费已超过30分钟，请重新缴费后再出场'},
                        status=status.HTTP_402_PAYMENT_REQUIRED,
                    )
            else:
                return Response(
                    {'detail': '请先完成缴费后再出场', 'amount': float(session.amount or 0)},
                    status=status.HTTP_402_PAYMENT_REQUIRED,
                )

        session.exit_time = timezone.now()
        session.save(update_fields=['exit_time'])

        if session.spot:
            session.spot.current_plate = None
            session.spot.pending_exit_plate = None
            session.spot.pending_exit_time = None
            session.spot.bind_time = None
            session.spot.save(update_fields=['current_plate', 'pending_exit_plate', 'pending_exit_time', 'bind_time'])

        return Response({
            'detail': '出场成功',
            'exit_time': session.exit_time.isoformat(),
            'subscription_free': has_active_sub,
        })

    @action(detail=False, methods=['post'], url_path='mark-exit-by-plate')
    @permission_classes([permissions.AllowAny])
    def mark_exit_by_plate(self, request):
        """通过车牌号直接标记出场（无 session_id 的场景）。"""
        from accounts.models import Vehicle

        plate = request.data.get('plate_number', '').strip().upper()
        if not plate:
            return Response({'detail': '缺少 plate_number 参数'}, status=status.HTTP_400_BAD_REQUEST)

        # 查找车位
        spot = ParkingSpace.objects.filter(
            current_plate__iexact=plate
        ).exclude(current_plate__isnull=True).exclude(current_plate='').first()

        if not spot:
            return Response({'detail': '未找到该车位'}, status=status.HTTP_404_NOT_FOUND)

        # 检查是否已缴费
        if spot.pending_exit_plate and spot.pending_exit_time:
            elapsed = (timezone.now() - spot.pending_exit_time).total_seconds()
            if elapsed > 1800:  # 超过30分钟
                spot.pending_exit_plate = None
                spot.pending_exit_time = None
                spot.save(update_fields=['pending_exit_plate', 'pending_exit_time'])
                return Response(
                    {'detail': '缴费已超过30分钟，请重新缴费后再出场'},
                    status=status.HTTP_402_PAYMENT_REQUIRED,
                )
        else:
            return Response(
                {'detail': '请先完成缴费后再出场'},
                status=status.HTTP_402_PAYMENT_REQUIRED,
            )

        # 清除车位信息
        spot.current_plate = None
        spot.pending_exit_plate = None
        spot.pending_exit_time = None
        spot.bind_time = None
        spot.save(update_fields=['current_plate', 'pending_exit_plate', 'pending_exit_time', 'bind_time'])

        return Response({
            'detail': '出场成功',
            'exit_time': timezone.now().isoformat(),
        })


class ReservationViewSet(viewsets.ModelViewSet):
    """
    车位预约 — 对应 _13 预约流程 + _5 预订记录

    用户端：只看自己的预约
    管理端：查看所有预约
    """
    serializer_class = ReservationSerializer
    filterset_fields = ['status', 'date']
    search_fields = ['booking_code', 'spot__space_id']
    ordering_fields = ['date', 'start_time', 'created_at']

    def get_queryset(self):
        user = self.request.user
        qs = Reservation.objects.all()
        if not user.is_staff:
            qs = qs.filter(user=user)

        # 自动将已过期的预约标记为 expired
        now = timezone.now()
        qs.filter(
            status__in=[Reservation.Status.PENDING, Reservation.Status.CONFIRMED],
            end_date__lt=now.date(),
        ).update(status=Reservation.Status.EXPIRED)
        qs.filter(
            status__in=[Reservation.Status.PENDING, Reservation.Status.CONFIRMED],
            end_date=now.date(),
            end_time__lt=now.time(),
        ).update(status=Reservation.Status.EXPIRED)

        return qs

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        """
        取消预约 — 对应 _13 规则说明 "开始前2小时可免费取消"

        POST /api/v1/parking/reservations/{id}/cancel/
        """
        reservation = self.get_object()
        if reservation.status in (Reservation.Status.COMPLETED, Reservation.Status.CANCELLED):
            return Response(
                {'detail': '该预约无法取消'},
                status=status.HTTP_400_BAD_REQUEST
            )
        reservation.status = Reservation.Status.CANCELLED
        # 释放车位
        if reservation.spot:
            reservation.spot.reserved_plate = None
            reservation.spot.save(update_fields=['reserved_plate', 'last_updated'])
        reservation.save(update_fields=['status'])
        return Response({'detail': '预约已取消', 'status': reservation.status})


class SpotConnectionViewSet(viewsets.ModelViewSet):
    """
    停车位连接管理 — Dijkstra 路径规划用

    管理员端：添加/编辑/删除停车位间的导航关系
    用户端：只读查看
    """
    serializer_class = SpotConnectionSerializer
    queryset = SpotConnection.objects.all()
    filterset_fields = ['from_spot', 'to_spot']

    def get_permissions(self):
        """管理端允许增删改，用户端只读"""
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


class NavigationViewSet(viewsets.ViewSet):
    """
    导航路径规划 — 使用 Dijkstra 算法计算停车场中的最短路径

    端点：
    - POST /api/v1/parking/navigation/find-path/
      请求：{start_spot_id: int, end_spot_id: int}
      返回：{path: [...], distance: float, steps: [...]}
    """
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['post'], url_path='find-path')
    def find_path(self, request):
        """
        计算两个停车位间的最短导航路径

        POST /api/v1/parking/navigation/find-path/

        请求体：
        {
            "start_spot_id": 1,
            "end_spot_id": 5
        }

        响应：
        {
            "path": ["A-01", "A-02", "B-02", "B-05"],
            "distance": 45.5,
            "steps": [
                {
                    "from": "A-01",
                    "to": "A-02",
                    "distance": 1.5,
                    "from_coords": [100, 200],
                    "to_coords": [150, 200]
                },
                ...
            ]
        }

        错误响应：
        {
            "error": "起点或终点不存在",
            "error_code": "invalid_spots"
        }
        {
            "error": "无法到达终点停车位",
            "error_code": "unreachable"
        }
        """
        start_spot_id = request.data.get('start_spot_id')
        end_spot_id = request.data.get('end_spot_id')

        if not start_spot_id or not end_spot_id:
            return Response(
                {'error': '缺少 start_spot_id 或 end_spot_id', 'error_code': 'missing_params'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            start_spot_id = int(start_spot_id)
            end_spot_id = int(end_spot_id)
        except (ValueError, TypeError):
            return Response(
                {'error': '停车位 ID 必须为整数', 'error_code': 'invalid_type'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 验证停车位存在
        try:
            start_spot = ParkingSpace.objects.get(id=start_spot_id)
            end_spot = ParkingSpace.objects.get(id=end_spot_id)
        except ParkingSpace.DoesNotExist:
            return Response(
                {'error': '起点或终点停车位不存在', 'error_code': 'invalid_spots'},
                status=status.HTTP_404_NOT_FOUND
            )

        # 计算路径 — 优先使用图搜索（Dijkstra），图不可达时回退到直接路径
        path_result = find_path(start_spot_id, end_spot_id)

        if path_result is None:
            path_result = _compute_direct_path(start_spot, end_spot)

        serializer = NavigationPathSerializer(path_result)
        return Response(serializer.data)


# ============================================================================
# 室内交互地图与反向寻车模块 (Interactive Indoor Map & Reverse Car Finding)
# ============================================================================

class MapViewSet(viewsets.ViewSet):
    """
    室内交互地图 API — PRD Section 3 (Interactive Indoor Map Module)
    
    提供前端 SVG 地图所需的数据接口：
    - GET /api/v1/map/spaces/           获取全量车位状态
    - GET /api/v1/map/find_car/         根据车牌号寻车
    """
    permission_classes = [permissions.AllowAny]

    @staticmethod
    def _normalize_plate(value):
        if not value:
            return ''
        return str(value).upper().replace('·', '').replace('.', '').replace(' ', '').strip()

    @classmethod
    def _is_plate_match(cls, candidate, query):
        cand = cls._normalize_plate(candidate)
        q = cls._normalize_plate(query)
        if not cand or not q:
            return False
        # 支持完整车牌匹配和后5-6位后缀搜索或模糊匹配
        return q in cand

    @action(detail=False, methods=['get'], url_path='spaces')
    def get_spaces(self, request):
        """
        获取全局车位状态 — 需求文档 Section 3.3 (Backend Specifications)
        
        端点：GET /api/v1/map/spaces/
        
        用途：前端初始化 SVG 地图时调用，获取所有车位的实时状态
        
        响应格式：
        {
            "code": 200,
            "data": [
                {"space_id": "space_A001", "status": "occupied"},
                {"space_id": "space_A002", "status": "free"},
                ...
            ]
        }
        
        状态值说明（需求文档 Section 3.2）：
        - 'free': 空闲 (填充色 #e0f7fa)
        - 'occupied': 占用 (填充色 #ffebee)
        """
        floor = request.query_params.get('floor')
        # 同时返回车位和地点节点（电梯/出入口等），前端需要地点节点作为导航起点
        spaces = ParkingSpace.objects.all().order_by('space_id')
        if floor:
            spaces = spaces.filter(floor=floor)

        serializer = ParkingSpaceSerializer(spaces, many=True)
        
        response_data = {
            'code': 200,
            'data': serializer.data
        }
        
        return Response(response_data)

    @action(detail=False, methods=['get'], url_path='start-points')
    def get_start_points(self, request):
        """获取可选导航起点（电梯口/出入口/服务台等地点节点）。"""
        floor = request.query_params.get('floor')
        qs = ParkingSpace.objects.filter(node_type=ParkingSpace.NodeType.LOCATION).order_by('floor', 'space_id')
        if floor:
            qs = qs.filter(floor=floor)

        serializer = NavigationStartPointSerializer(qs, many=True)
        return Response({'code': 200, 'data': serializer.data})

    @action(detail=False, methods=['get'], url_path='find_car')
    def find_car(self, request):
        """
        寻车查询接口 — PRD Section 6.2
        
        支持通过 车牌号 (plate_number) 或 车位号 (space_id) 查询目标点。
        
        端点：GET /api/v1/map/find_car/?plate_number=京A88888 或 ?space_id=space_A001
        """
        plate_query = request.query_params.get('plate_number')
        space_query = request.query_params.get('space_id')
        floor = request.query_params.get('floor')
        
        if not plate_query and not space_query:
            return Response(
                {
                    'code': 400,
                    'error': '请提供车牌号 (plate_number) 或车位号 (space_id)'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        parking_space = None

        # 优先按车位号精准查询
        if space_query:
            qs = ParkingSpace.objects.filter(space_id=space_query.strip())
            if floor:
                qs = qs.filter(floor=floor)
            parking_space = qs.first()
            if not parking_space:
                return Response(
                    {'code': 404, 'error': f'未找到编号为 "{space_query}" 的车位'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # 否则按车牌号模糊查询
        elif plate_query:
            spaces = ParkingSpace.objects.filter(node_type=ParkingSpace.NodeType.PARKING).exclude(current_plate__isnull=True).exclude(current_plate='')
            if floor:
                spaces = spaces.filter(floor=floor)

            query_norm = self._normalize_plate(plate_query)
            for item in spaces.iterator():
                if self._is_plate_match(item.current_plate, query_norm):
                    parking_space = item
                    break

            if not parking_space:
                return Response(
                    {
                        'code': 404,
                        'error': f'未找到车牌号 "{plate_query}" 的停车记录'
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

        location_desc = f'{parking_space.floor} {parking_space.space_id}' if parking_space.floor else parking_space.space_id

        response_data = {
            'code': 200,
            'data': {
                'plate_number': parking_space.current_plate or '',
                'spot_id': parking_space.id,
                'space_id': parking_space.space_id,
                'floor': parking_space.floor,
                'location_desc': location_desc
            }
        }

        return Response(response_data)


class HardwareWebhookViewSet(viewsets.ViewSet):
    """
    硬件推送 WebHook — PRD Section 3.3 (Backend Specifications)
    
    接收虚拟停车场硬件（如停车位传感器、入出口闸机）推送的事件，
    实时更新车位状态数据库。
    
    端点：POST /api/v1/hardware/webhook/
    """
    permission_classes = [permissions.AllowAny]  # 实际应在生产环境中验证硬件身份

    @action(detail=False, methods=['post'], url_path='webhook')
    def handle_webhook(self, request):
        """
        处理硬件推送的车位变化事件
        
        端点：POST /api/v1/hardware/webhook/
        
        请求体示例：
        {
            "event_type": "space_occupied",  // space_occupied | space_released | space_maintenance
            "space_id": "space_A001",
            "plate_number": "京A88888",      // 占用时提供
            "timestamp": "2026-04-19T14:30:00Z"
        }
        
        功能：
        1. 验证请求合法性
        2. 更新 ParkingSpace 表的状态
        3. 如果有关联的 ParkingSpot，也更新其状态
        4. 返回确认响应
        """
        event_type = request.data.get('event_type')
        space_id = request.data.get('space_id')
        plate_number = request.data.get('plate_number')

        # 参数验证
        if not space_id or not event_type:
            return Response(
                {
                    'code': 400,
                    'error': '缺少 space_id 或 event_type 参数'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # 获取车位对象
        parking_space = get_object_or_404(ParkingSpace, space_id=space_id)

        # 根据事件类型更新状态
        if event_type == 'space_occupied':
            parking_space.current_plate = plate_number

            # 创建停车会话
            from accounts.models import Vehicle
            from decimal import Decimal
            from payments.models import Subscription
            vehicle = Vehicle.objects.filter(plate_number__iexact=plate_number or '').first()

            # 模拟场景：车辆未注册时自动创建，使进出场流程闭环
            if not vehicle and plate_number:
                owner = None
                if request.user.is_authenticated:
                    owner = request.user
                if owner is None:
                    from accounts.models import User
                    owner = User.objects.filter(is_staff=True).order_by('id').first()
                if owner:
                    vehicle = Vehicle.objects.create(
                        owner=owner,
                        plate_number=plate_number,
                        brand='模拟车辆',
                        model='自动创建',
                        is_simulated=True,
                    )

            if vehicle:
                today = timezone.localdate()
                has_active_sub = Subscription.objects.filter(
                    user=vehicle.owner,
                    is_active=True,
                    start_date__lte=today,
                    end_date__gte=today,
                ).exists()
                ParkingSession.objects.create(
                    vehicle=vehicle,
                    spot=parking_space,
                    entry_time=timezone.now(),
                    amount=Decimal('0'),
                    payment_status=(
                        ParkingSession.PaymentStatus.PAID
                        if has_active_sub
                        else ParkingSession.PaymentStatus.PENDING
                    ),
                )

        elif event_type == 'space_released':
            # 关闭对应的活跃会话
            from accounts.models import Vehicle
            vehicle = None
            if plate_number:
                vehicle = Vehicle.objects.filter(plate_number__iexact=plate_number).first()
            if vehicle:
                active_session = ParkingSession.objects.filter(
                    vehicle=vehicle,
                    exit_time__isnull=True,
                ).order_by('-entry_time').first()
            else:
                # 无车牌时按车位关闭最近的活跃会话
                active_session = ParkingSession.objects.filter(
                    spot=parking_space,
                    exit_time__isnull=True,
                ).order_by('-entry_time').first()
            if active_session:
                active_session.exit_time = timezone.now()
                active_session.save(update_fields=['exit_time'])
            parking_space.current_plate = None
        elif event_type == 'space_maintenance':
            parking_space.status = True
        else:
            return Response(
                {
                    'code': 400,
                    'error': f'未知的事件类型: {event_type}'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        parking_space.save()
        return Response(
            {
                'code': 200,
                'message': f'车位 {space_id} 状态已更新',
                'space_id': space_id,
                'status': 'occupied' if parking_space.current_plate else 'free',
                'timestamp': parking_space.last_updated.isoformat()
            },
            status=status.HTTP_200_OK
        )


def get_map_svg(request):
    """读取并返回真实停车场 SVG 底图。"""
    svg_path = Path(__file__).resolve().parents[2] / 'svg' / 'interactive_map.svg'

    if not svg_path.exists():
        return JsonResponse(
            {'code': 404, 'error': f'SVG 底图不存在: {svg_path.name}'},
            status=404
        )

    try:
        svg_content = svg_path.read_text(encoding='utf-8')
    except Exception as exc:
        return JsonResponse(
            {'code': 500, 'error': f'读取 SVG 失败: {exc}'},
            status=500
        )

    return JsonResponse({'code': 200, 'data': {'svg': svg_content}})
