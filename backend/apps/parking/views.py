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
        """根据车牌号查询当前活跃停车会话（首页快速缴费·无需登录查询）。"""
        plate = request.query_params.get('plate', '').strip().upper()
        if not plate:
            return Response({'detail': '缺少 plate 参数'}, status=status.HTTP_400_BAD_REQUEST)

        from accounts.models import Vehicle, User
        from payments.models import PricingRule, Subscription

        vehicle = Vehicle.objects.filter(plate_number__iexact=plate).first()
        session = None

        if vehicle:
            session = ParkingSession.objects.filter(
                vehicle=vehicle, exit_time__isnull=True
            ).first()

        # 兜底：车辆未注册或无会话时，检查是否有车位记录了该车牌（模拟进场遗留）
        if not session:
            space_with_plate = ParkingSpace.objects.filter(
                current_plate__iexact=plate
            ).exclude(current_plate__isnull=True).exclude(current_plate='').first()

            if space_with_plate:
                # 自动创建车辆（若不存在）
                if not vehicle:
                    owner = request.user if request.user.is_authenticated else None
                    if owner is None:
                        owner = User.objects.filter(is_staff=True).order_by('id').first()
                    if owner:
                        vehicle = Vehicle.objects.create(
                            owner=owner,
                            plate_number=plate,
                            brand='模拟车辆',
                            model='自动创建',
                        )

                # 自动创建会话
                if vehicle:
                    session = ParkingSession.objects.create(
                        vehicle=vehicle,
                        spot=space_with_plate,
                        entry_time=space_with_plate.bind_time or space_with_plate.last_updated or timezone.now(),
                        amount=None,
                        payment_status=ParkingSession.PaymentStatus.PENDING,
                    )

        if not session:
            return Response({'found': False, 'detail': '该车辆当前无停车会话'}, status=status.HTTP_404_NOT_FOUND)

        # 检查车主是否有有效订阅
        today = timezone.localdate()
        has_active_sub = Subscription.objects.filter(
            user=vehicle.owner,
            is_active=True,
            start_date__lte=today,
            end_date__gte=today,
        ).exists()

        # 有订阅则自动标记免费
        if has_active_sub and session.payment_status != ParkingSession.PaymentStatus.PAID:
            session.amount = 0
            session.payment_status = ParkingSession.PaymentStatus.PAID
            session.save(update_fields=['amount', 'payment_status'])

        now = timezone.now()
        duration = now - session.entry_time
        total_minutes = int(duration.total_seconds() / 60)
        hours = total_minutes // 60
        mins = total_minutes % 60
        chargeable_hours = max(1, hours + (1 if mins > 0 else 0))

        # 计算应缴金额：若已存储金额则使用，否则按定价规则实时计算
        amount = session.amount
        if amount is None:
            hourly_rate = PricingRule.get_active_value(
                PricingRule.RateType.HOURLY_STANDARD, Decimal('6.00')
            ) or Decimal('6.00')
            amount = hourly_rate * chargeable_hours

        return Response({
            'session_id': session.id,
            'plate_number': vehicle.plate_number,
            'entry_time': session.entry_time.isoformat(),
            'duration_text': f'{hours}小时{mins}分钟',
            'chargeable_hours': chargeable_hours,
            'amount': float(amount or 0),
            'payment_state': session.payment_status,
            'found': True,
            'subscription_free': has_active_sub,
        })

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
        transaction_id = f"QUICK_{int(time.time() * 1000)}"
        payment = Payment.objects.create(
            user=request.user if request.user.is_authenticated else None,
            transaction_id=transaction_id,
            amount=amount_dec,
            method=method,
            status=Payment.Status.PENDING,
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

    @action(detail=True, methods=['post'], url_path='mark-exit')
    @permission_classes([permissions.AllowAny])
    def mark_exit(self, request, pk=None):
        """标记车辆出场（首页模拟出场）。"""
        session = self.get_object()
        if session.exit_time:
            return Response({'detail': '车辆已出场', 'exit_time': session.exit_time.isoformat()})

        session.exit_time = timezone.now()
        session.save(update_fields=['exit_time'])

        if session.spot:
            session.spot.current_plate = None
            session.spot.bind_time = None
            session.spot.save(update_fields=['current_plate', 'bind_time'])

        return Response({'detail': '出场成功', 'exit_time': session.exit_time.isoformat()})


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

        # 计算路径
        path_result = find_path(start_spot_id, end_spot_id)

        if path_result is None:
            return Response(
                {
                    'error': f'无法从 {start_spot.space_id} 到达 {end_spot.space_id}',
                    'error_code': 'unreachable',
                    'start': start_spot.space_id,
                    'end': end_spot.space_id,
                },
                status=status.HTTP_404_NOT_FOUND
            )

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
        spaces = ParkingSpace.objects.filter(node_type=ParkingSpace.NodeType.PARKING).order_by('space_id')
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
            from payments.models import Subscription
            vehicle = Vehicle.objects.filter(plate_number__iexact=plate_number or '').first()

            # 模拟场景：车辆未注册时自动创建，使进出场流程闭环
            if not vehicle and plate_number:
                owner = request.user if request.user.is_authenticated else None
                if owner is None:
                    from accounts.models import User
                    owner = User.objects.filter(is_staff=True).order_by('id').first()
                if owner:
                    vehicle = Vehicle.objects.create(
                        owner=owner,
                        plate_number=plate_number,
                        brand='模拟车辆',
                        model='自动创建',
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
                    amount=0 if has_active_sub else None,
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
