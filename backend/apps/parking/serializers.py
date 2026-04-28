"""
parking — 序列化器

前后端字段对齐：
- ParkingSession → _4 当前会话卡片 + _9 交易记录
- Reservation → _13 预约流程 + _5 预订记录
- ParkingSpace → 室内交互地图渲染数据

新增（室内地图与反向寻车模块）：
- ParkingSpaceSerializer: SVG 地图所需的简化车位数据
- MapSpacesResponseSerializer: 地图全量状态接口的响应格式
- FindCarResponseSerializer: 反向寻车接口的响应格式
"""

from datetime import datetime
from decimal import Decimal, ROUND_CEILING
from django.db import transaction
from django.db.models import Q

from rest_framework import serializers
from accounts.models import Vehicle
from .models import ParkingSession, Reservation, SpotConnection, ParkingSpace
from payments.models import PricingRule


class ParkingSpotSerializer(serializers.ModelSerializer):
    """
    车位信息 — 对应 _2 地图网格 + _8 管理后台表格

    地图网格需要的字段：spot_id, status, spot_type, floor_x, floor_y
    管理后台表格列：车位ID, 状态, 类型, 楼层, 区域
    """

    # 兼容旧接口字段，底层使用 ParkingSpace
    spot_id = serializers.CharField(source='space_id', read_only=True)
    zone = serializers.SerializerMethodField()
    spot_type = serializers.SerializerMethodField()
    spot_type_label = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    status_label = serializers.SerializerMethodField()
    floor_x = serializers.FloatField(source='x', read_only=True)
    floor_y = serializers.FloatField(source='y', read_only=True)
    updated_at = serializers.DateTimeField(source='last_updated', read_only=True)

    class Meta:
        model = ParkingSpace
        fields = [
            'id', 'spot_id', 'floor', 'zone', 'spot_type', 'spot_type_label',
            'status', 'status_label', 'floor_x', 'floor_y',
            'node_type', 'location_name', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_zone(self, obj):
        if not obj.space_id:
            return ''
        try:
            return obj.space_id.split('_', 1)[1][0]
        except Exception:
            return ''

    def get_spot_type(self, obj):
        return 'ev' if obj.type else 'standard'

    def get_spot_type_label(self, obj):
        return '充电桩' if obj.type else '标准'

    def get_status(self, obj):
        if obj.status:
            return 'maintenance'
        has_reserved_plate = bool(str(obj.reserved_plate or '').strip())
        if has_reserved_plate and not obj.current_plate:
            return 'reserved'
        if obj.current_plate:
            return 'occupied'
        return 'free'

    def get_status_label(self, obj):
        mapping = {
            'maintenance': '维修中',
            'reserved': '已预约',
            'occupied': '已占用',
            'free': '空闲',
        }
        return mapping[self.get_status(obj)]

    def get_node_type(self, obj):
        return obj.node_type

    def get_location_name(self, obj):
        return obj.location_name or ''


class ParkingSessionSerializer(serializers.ModelSerializer):
    """
    停车会话 — 对应 _4 当前停车卡片

    卡片展示需要：车牌号、车位编号、入场时间、时长、金额、支付状态
    """

    # 嵌套只读字段 — 前端卡片需要车牌号和车位编号
    plate_number = serializers.CharField(
        source='vehicle.plate_number', read_only=True
    )
    spot_id = serializers.CharField(
        source='spot.space_id', read_only=True
    )
    payment_status_label = serializers.CharField(
        source='get_payment_status_display', read_only=True
    )
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = ParkingSession
        fields = [
            'id', 'vehicle', 'plate_number', 'spot', 'spot_id',
            'entry_time', 'exit_time', 'amount',
            'payment_status', 'payment_status_label',
            'is_active', 'created_at',
        ]
        read_only_fields = ['id', 'amount', 'created_at']


class ReservationSerializer(serializers.ModelSerializer):
    """
    车位预约 — 对应 _13 预约流程

    汇总卡片需要：车位编号、日期、时间段、总费用、预约码
    """

    spot_id = serializers.CharField(
        source='spot.space_id', read_only=True
    )
    spot_floor = serializers.CharField(
        source='spot.floor', read_only=True
    )
    spot_detail = serializers.SerializerMethodField()
    status_label = serializers.CharField(
        source='get_status_display', read_only=True
    )
    payment_method = serializers.CharField(write_only=True, required=False, allow_blank=True)
    payment_transaction_id = serializers.CharField(write_only=True, required=False, allow_blank=True)
    vehicle = serializers.PrimaryKeyRelatedField(queryset=Vehicle.objects.all(), write_only=True, required=False, allow_null=True)
    preferred_floor = serializers.CharField(write_only=True, required=False, allow_blank=True)
    spot_type = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Reservation
        fields = [
            'id', 'user', 'spot', 'spot_id', 'spot_floor',
            'spot_detail',
            'date', 'end_date', 'start_time', 'end_time',
            'payment_method',
            'payment_transaction_id',
            'vehicle',
            'preferred_floor', 'spot_type',
            'total_amount', 'booking_code', 'qr_code',
            'status', 'status_label',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'user', 'booking_code', 'qr_code',
            'created_at', 'updated_at',
        ]
        extra_kwargs = {
            'spot': {'required': False},
        }

    def get_spot_detail(self, obj):
        if not obj.spot:
            return None
        raw_id = obj.spot.space_id or ''
        display_id = raw_id.replace('space_', '')
        zone = ''
        if '_' in raw_id:
            suffix = raw_id.split('_', 1)[1]
            zone = suffix[0] if suffix else ''

        return {
            'floor': obj.spot.floor,
            'zone': zone,
            'spot_id': display_id,
            'space_id': raw_id,
        }

    def validate(self, attrs):
        date = attrs.get('date')
        end_date = attrs.get('end_date') or date
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')
        spot = attrs.get('spot')
        preferred_floor = (attrs.get('preferred_floor') or '').strip()
        spot_type = (attrs.get('spot_type') or '').strip().lower()

        if preferred_floor and preferred_floor not in [choice[0] for choice in ParkingSpace.Floor.choices]:
            raise serializers.ValidationError({'preferred_floor': '不支持的楼层选项'})

        if spot_type and spot_type not in ('standard', 'ev'):
            raise serializers.ValidationError({'spot_type': '不支持的车位类型选项'})

        if spot is not None:
            if spot.status:
                raise serializers.ValidationError({'spot': '该车位处于维修状态，无法预约'})
            if str(spot.reserved_plate or '').strip():
                raise serializers.ValidationError({'spot': '该车位已被预约，请选择其他车位'})
            if str(spot.current_plate or '').strip():
                raise serializers.ValidationError({'spot': '该车位已被占用，请选择其他车位'})

            if preferred_floor and spot.floor != preferred_floor:
                raise serializers.ValidationError({'spot': '指定车位与所选楼层不一致'})

            if spot_type == 'ev' and not spot.type:
                raise serializers.ValidationError({'spot': '指定车位不是充电桩车位'})
            if spot_type == 'standard' and spot.type:
                raise serializers.ValidationError({'spot': '指定车位不是标准车位'})

        if date and start_time and end_time:
            attrs['end_date'] = end_date
            if end_date < date:
                raise serializers.ValidationError({'end_date': '离开日期不能早于入场日期'})

            start_dt = datetime.combine(date, start_time)
            end_dt = datetime.combine(date, end_time)
            if end_dt <= start_dt:
                raise serializers.ValidationError({'end_time': '结束时间必须晚于开始时间'})

            billing_days = max(1, (end_date - date).days + 1)

            daily_rate = PricingRule.get_active_value(PricingRule.RateType.RESERVATION_DAILY, Decimal('30.00')) or Decimal('30.00')
            ev_surcharge = PricingRule.get_active_value(PricingRule.RateType.RESERVATION_EV_SURCHARGE, Decimal('10.00')) or Decimal('0.00')
            base_amount = daily_rate * billing_days
            is_ev_reservation = (spot and spot.type) or (spot is None and spot_type == 'ev')
            ev_surcharge = ev_surcharge if is_ev_reservation else Decimal('0.00')
            attrs['total_amount'] = (base_amount + ev_surcharge).quantize(Decimal('0.01'))

        return attrs

    def create(self, validated_data):
        import uuid

        # 预约附加参数：支付方式/支付流水号/车辆偏好
        payment_method = (validated_data.pop('payment_method', '') or '').strip()
        payment_transaction_id = (validated_data.pop('payment_transaction_id', '') or '').strip()
        vehicle = validated_data.pop('vehicle', None)
        preferred_floor = (validated_data.pop('preferred_floor', '') or '').strip()
        spot_type = (validated_data.pop('spot_type', '') or '').strip().lower()

        with transaction.atomic():
            spot = validated_data.get('spot')
            if spot is None:
                spot_qs = ParkingSpace.objects.select_for_update().filter(
                    status=False,
                ).filter(Q(reserved_plate__isnull=True) | Q(reserved_plate='')).filter(
                    Q(current_plate__isnull=True) | Q(current_plate='')
                )

                if preferred_floor:
                    spot_qs = spot_qs.filter(floor=preferred_floor)

                if spot_type in ('standard', 'ev'):
                    spot_qs = spot_qs.filter(type=(spot_type == 'ev'))

                spot = spot_qs.order_by('id').first()
                if spot is None:
                    raise serializers.ValidationError({'detail': '所选条件下暂无可用车位，请更换楼层或类型后重试'})
                validated_data['spot'] = spot
            else:
                locked_spot = ParkingSpace.objects.select_for_update().filter(id=spot.id).first()
                if locked_spot is None:
                    raise serializers.ValidationError({'spot': '指定车位不存在或已失效'})

                if locked_spot.status:
                    raise serializers.ValidationError({'spot': '该车位处于维修状态，无法预约'})
                if str(locked_spot.reserved_plate or '').strip():
                    raise serializers.ValidationError({'spot': '该车位已被预约，请选择其他车位'})
                if str(locked_spot.current_plate or '').strip():
                    raise serializers.ValidationError({'spot': '该车位已被占用，请选择其他车位'})

                if preferred_floor and locked_spot.floor != preferred_floor:
                    raise serializers.ValidationError({'spot': '指定车位与所选楼层不一致'})

                if spot_type == 'ev' and not locked_spot.type:
                    raise serializers.ValidationError({'spot': '指定车位不是充电桩车位'})
                if spot_type == 'standard' and locked_spot.type:
                    raise serializers.ValidationError({'spot': '指定车位不是标准车位'})

                validated_data['spot'] = locked_spot

            validated_data['user'] = self.context['request'].user
            validated_data['payment_method'] = payment_method
            validated_data['payment_transaction_id'] = payment_transaction_id
            validated_data['booking_code'] = f'SENT-{uuid.uuid4().hex[:6].upper()}'
            reservation = super().create(validated_data)

            reserved_plate = ''
            request_user = self.context['request'].user
            if vehicle is not None:
                vehicle = Vehicle.objects.filter(id=vehicle.id, owner=request_user).first()
                if vehicle is None:
                    raise serializers.ValidationError({'vehicle': '请选择当前账号下的车辆'})
                reserved_plate = vehicle.plate_number
            else:
                fallback_vehicle = Vehicle.objects.filter(owner=request_user).order_by('-is_primary', '-id').first()
                if fallback_vehicle is not None:
                    reserved_plate = fallback_vehicle.plate_number

            if reservation.spot and not str(reservation.spot.reserved_plate or '').strip():
                if reserved_plate:
                    reservation.spot.reserved_plate = reserved_plate
                    reservation.spot.save(update_fields=['reserved_plate', 'last_updated'])
                else:
                    reservation.spot.reserved_plate = 'RESERVED'
                    reservation.spot.save(update_fields=['reserved_plate', 'last_updated'])

            return reservation


class SpotConnectionSerializer(serializers.ModelSerializer):
    """
    停车位连接 — Dijkstra 路径规划用

    存储两个车位间的导航关系和距离
    """

    from_spot_id = serializers.CharField(
        source='from_spot.space_id', read_only=True
    )
    to_spot_id = serializers.CharField(
        source='to_spot.space_id', read_only=True
    )

    class Meta:
        model = SpotConnection
        fields = [
            'id', 'from_spot', 'to_spot',
            'from_spot_id', 'to_spot_id',
            'distance',
        ]
        read_only_fields = ['id']


class NavigationPathSerializer(serializers.Serializer):
    """
    路径规划结果 — 返回给前端的导航信息
    """

    path = serializers.ListField(
        child=serializers.CharField(),
        help_text='停车位编号序列 [A-01, A-02, B-02, ...]'
    )
    path_node_ids = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text='路径节点唯一ID序列 [space_A001, loc_elevator_a, ...]'
    )
    path_points = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        help_text='连续坐标点序列 [{x: 10.2, y: 33.1}, ...]'
    )
    distance = serializers.FloatField(
        help_text='总导航距离（米）'
    )
    steps = serializers.ListField(
        child=serializers.DictField(),
        help_text='导航步骤详情'
    )

    def create(self, validated_data: dict) -> Reservation:
        """创建预约时自动关联当前用户 + 生成预约编号"""
        import uuid
        validated_data['user'] = self.context['request'].user
        validated_data['booking_code'] = f'SENT-{uuid.uuid4().hex[:6].upper()}'
        return super().create(validated_data)


# ============================================================================
# 室内交互地图与反向寻车模块 (Interactive Indoor Map & Reverse Car Finding)
# ============================================================================

class ParkingSpaceSerializer(serializers.ModelSerializer):
    """
    车位信息序列化器 — 对应 PRD Section 3.2 (Frontend Specifications)
    
    用途：为前端 SVG 地图提供简化的车位状态数据
    返回字段：space_id, status, current_plate, center_x, center_y, x, y, floor, rotation
    """
    
    status = serializers.SerializerMethodField()
    is_damaged = serializers.BooleanField(source='status', read_only=True)

    class Meta:
        model = ParkingSpace
        fields = [
            'id', 'space_id', 'floor', 'node_type', 'location_name', 'status', 'is_damaged', 'type', 'reserved_plate', 'current_plate',
            'x', 'y', 'center_x', 'center_y', 'rotation', 'last_updated'
        ]
        read_only_fields = fields

    def get_status(self, obj):
        """地图状态：维修 > 占用 > 已预约 > 空闲。"""
        if obj.status:
            return 'maintenance'
        has_reserved_plate = bool(str(obj.reserved_plate or '').strip())
        if has_reserved_plate:
            return 'reserved'
        if obj.current_plate:
            return 'occupied'
        return 'free'


class MapSpacesResponseSerializer(serializers.Serializer):
    """
    地图全量状态响应 — 对应 PRD Section 6.1 (Get Global Parking Status)
    
    返回格式：
    {
        "code": 200,
        "data": [
            {"space_id": "space_A001", "status": 1},
            {"space_id": "space_A002", "status": 0},
            ...
        ]
    }
    """
    
    code = serializers.IntegerField(default=200)
    data = serializers.ListField(
        child=serializers.DictField(),
        help_text='车位状态列表'
    )


class FindCarResponseSerializer(serializers.Serializer):
    """
    寻车查询响应 — 对应 PRD Section 6.2 (Car Finding Query)
    
    用途：根据车牌号查询车所在位置
    
    返回格式：
    {
        "code": 200,
        "data": {
            "plate_number": "京A88888",
            "space_id": "space_A001",
            "location_desc": "A区 001号车位"
        }
    }
    """
    
    code = serializers.IntegerField(default=200)
    data = serializers.DictField(
        child=serializers.CharField(),
        help_text='包含 plate_number, space_id, location_desc'
    )


class NavigationStartPointSerializer(serializers.ModelSerializer):
    """反向寻车导航起点列表序列化器。"""

    label = serializers.SerializerMethodField()

    class Meta:
        model = ParkingSpace
        fields = ['id', 'space_id', 'floor', 'label', 'center_x', 'center_y', 'node_type', 'location_name']
        read_only_fields = fields

    def get_label(self, obj):
        custom = str(obj.location_name or '').strip()
        return custom or obj.space_id
