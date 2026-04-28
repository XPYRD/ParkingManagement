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

from pathlib import Path
import re

from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from .models import ParkingSession, Reservation, SpotConnection, ParkingSpace
from payments.models import Subscription
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
        _PLATE_OCR_ENGINE = PaddleOCR(use_angle_cls=True, lang='ch')
    except Exception:
        _PLATE_OCR_ENGINE = False
    return _PLATE_OCR_ENGINE


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def ai_recognize_plate(request):
    """AI 车牌识别接口：供首页进场模拟上传图片识别使用。"""
    image_file = request.FILES.get('image')
    if not image_file:
        return Response({'detail': '缺少 image 文件'}, status=status.HTTP_400_BAD_REQUEST)

    # 兜底方案：先尝试从文件名中提取车牌
    filename_plate = _extract_plate_from_texts([getattr(image_file, 'name', '')])

    # 主方案：使用 OCR 识别
    ocr_plate = ''
    ocr_engine = _get_plate_ocr_engine()
    if ocr_engine:
        try:
            import numpy as np  # type: ignore
            import cv2  # type: ignore

            file_bytes = np.asarray(bytearray(image_file.read()), dtype=np.uint8)
            image_file.seek(0)
            image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            if image is not None:
                result = ocr_engine.ocr(image, cls=True)
                texts = []
                for block in result or []:
                    for line in block or []:
                        if isinstance(line, (list, tuple)) and len(line) >= 2:
                            rec = line[1]
                            if isinstance(rec, (list, tuple)) and rec:
                                texts.append(rec[0])
                ocr_plate = _extract_plate_from_texts(texts)
        except Exception:
            ocr_plate = ''

    plate_number = ocr_plate or filename_plate
    if not plate_number:
        return Response({
            'success': False,
            'detail': '未识别到车牌，请重试或手动输入',
            'plate_number': '',
        }, status=status.HTTP_200_OK)

    return Response({
        'success': True,
        'plate_number': plate_number,
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
    filterset_fields = ['floor', 'type', 'status']
    search_fields = ['space_id', 'current_plate']
    ordering_fields = ['spot_id', 'floor', 'status']

    @property
    def pagination_class(self):
        """地图场景传入 no_page=1 时取消分页，返回全量数据"""
        if self.request.query_params.get('no_page'):
            return None
        return super().pagination_class

    def get_permissions(self):
        """用户端只允许查看，管理端允许增删改"""
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


    @action(detail=False, methods=['get'], url_path='floor-summary')
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
            free = floor_qs.filter(status=False).filter(
                Q(reserved_plate__isnull=True) | Q(reserved_plate='')
            ).filter(Q(current_plate__isnull=True) | Q(current_plate='')).count()
            rate = round(occupied / total * 100, 1) if total > 0 else 0
            result.append({
                'floor': floor,
                'total': total,
                'free': free,
                'occupied': occupied,
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

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return ParkingSession.objects.all()
        # 用户端：只看自己车辆的会话
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
            sessions.filter().exclude(
                amount=0,
                payment_status=ParkingSession.PaymentStatus.PAID,
            ).update(
                amount=0,
                payment_status=ParkingSession.PaymentStatus.PAID,
            )

            sessions = self.get_queryset().filter(exit_time__isnull=True)
        serializer = self.get_serializer(sessions, many=True)
        return Response(serializer.data)


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
        if user.is_staff:
            return Reservation.objects.all()
        return Reservation.objects.filter(user=user)

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
        # 支持完整车牌匹配和后5-6位后缀搜索
        return cand == q or cand.endswith(q)

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
        elif event_type == 'space_released':
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
