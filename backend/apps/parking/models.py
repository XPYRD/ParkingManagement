"""parking 数据模型。"""

import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models


class ParkingSpace(models.Model):
    """室内地图车位对象。"""

    class NodeType(models.TextChoices):
        PARKING = 'parking', '车位'
        LOCATION = 'location', '地点'

    class Floor(models.TextChoices):
        B2 = 'B2', '地下二层'
        B1 = 'B1', '地下一层'
        F1 = '1F', '一楼'

    floor = models.CharField(
        max_length=10, choices=Floor.choices, default=Floor.B2,
        verbose_name='楼层', help_text='停车位所在楼层: B2/B1/1F'
    )
    space_id = models.CharField(
        max_length=50, verbose_name='车位编号(对应SVG ID)',
        help_text='如 space_A001, space_B005，与 SVG 元素 id 完全对应'
    )
    node_type = models.CharField(
        max_length=20,
        choices=NodeType.choices,
        default=NodeType.PARKING,
        verbose_name='节点类型',
        help_text='parking=真实车位, location=导航地点节点'
    )
    location_name = models.CharField(
        max_length=50,
        blank=True,
        default='',
        verbose_name='地点名称',
        help_text='地点节点名称，例如：电梯A、南出口、服务台'
    )
    qr_code_token = models.CharField(
        max_length=100, unique=True, blank=True, default='', verbose_name='二维码唯一识别码',
        help_text='二维码唯一识别码，用户扫描该二维码后绑定车牌'
    )
    status = models.BooleanField(
        default=False, verbose_name='是否损坏',
        help_text='true=损坏, false=正常'
    )
    type = models.BooleanField(
        default=False, verbose_name='是否充电桩停车位',
        help_text='true=充电桩停车位, false=普通停车位'
    )
    reserved_plate = models.CharField(
        max_length=20, null=True, blank=True, verbose_name='预约车牌',
        help_text='已预约车位对应的预约车牌号，不代表已实际占用'
    )
    current_plate = models.CharField(
        max_length=20, null=True, blank=True, verbose_name='当前停放车牌',
        help_text='若为空则表示车位空闲'
    )
    bind_time = models.DateTimeField(
        null=True, blank=True, verbose_name='绑定时间',
        help_text='用户绑定车牌的时间'
    )
    last_updated = models.DateTimeField(auto_now=True, verbose_name='最后状态更新时间')
    center_x = models.FloatField(null=True, blank=True, verbose_name='SVG X坐标', help_text='车位在 SVG 地图中的中心 X 坐标')
    center_y = models.FloatField(null=True, blank=True, verbose_name='SVG Y坐标', help_text='车位在 SVG 地图中的中心 Y 坐标')
    x = models.FloatField(null=True, blank=True, verbose_name='SVG相对坐标X', help_text='SVG相对坐标X，用于路径规划')
    y = models.FloatField(null=True, blank=True, verbose_name='SVG相对坐标Y', help_text='SVG相对坐标Y，用于路径规划')
    rotation = models.IntegerField(default=0, verbose_name='旋转角度', help_text='停车位旋转角度（0度 或 90度）')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'parking_space'
        verbose_name = '车位信息(地图渲染)'
        verbose_name_plural = '车位信息(地图渲染)'
        ordering = ['floor', 'space_id']
        unique_together = ['floor', 'space_id']
        indexes = [
            models.Index(fields=['node_type', 'floor']),
            models.Index(fields=['floor', 'status']),
            models.Index(fields=['floor', 'current_plate']),
        ]

    def __str__(self) -> str:
        if self.node_type == self.NodeType.LOCATION:
            return f'{self.floor}_{self.location_name or self.space_id} (地点)'
        damage_display = '损坏' if self.status else '正常'
        return f'{self.floor}_{self.space_id} ({damage_display})'

    def save(self, *args, **kwargs):
        if not self.qr_code_token:
            prefix = 'LOC' if self.node_type == self.NodeType.LOCATION else 'SPOT'
            self.qr_code_token = f'{prefix}-{uuid.uuid4().hex[:16].upper()}'
        super().save(*args, **kwargs)


class ParkingSession(models.Model):
    """
    停车会话 — 记录一次完整的入场→出场过程

    字段对照：
    ┌──────────────────┬──────────────────────────────────────────┐
    │ 字段             │ UI 来源                                   │
    ├──────────────────┼──────────────────────────────────────────┤
    │ vehicle          │ _4 当前会话卡片上方车牌号                    │
    │ spot             │ _4 "车位" 显示 "B2-15"                     │
    │ entry_time       │ _4 "入场时间" 显示 "上午 10:24"             │
    │ exit_time        │ _4 "时长" 推算                             │
    │ amount           │ _4 "金额" 显示 "¥18.50"                   │
    │ payment_status   │ _4 "未缴费" / "已支付" 标签                 │
    └──────────────────┴──────────────────────────────────────────┘
    """

    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', '未缴费'
        PAID = 'paid', '已支付'
        OVERSTAY = 'overstay', '超时待缴'

    vehicle = models.ForeignKey(
        'accounts.Vehicle', on_delete=models.CASCADE,
        related_name='sessions', verbose_name='车辆'
    )
    spot = models.ForeignKey(
        'ParkingSpace', on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='sessions', verbose_name='车位'
    )
    entry_time = models.DateTimeField('入场时间')
    exit_time = models.DateTimeField(
        '出场时间', null=True, blank=True,
        help_text='为空表示车辆仍在场内'
    )
    amount = models.DecimalField(
        '停车费用', max_digits=10, decimal_places=2, default=0,
        help_text='单位：元'
    )
    payment_status = models.CharField(
        '支付状态', max_length=10, choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '停车会话'
        verbose_name_plural = '停车会话'
        db_table = 'sentinel_parking_session'
        ordering = ['-entry_time']

    def __str__(self) -> str:
        return f'{self.vehicle} @ {self.spot} ({self.entry_time:%Y-%m-%d %H:%M})'

    @property
    def is_active(self) -> bool:
        """车辆是否仍在场内"""
        return self.exit_time is None


class Reservation(models.Model):
    """
    车位预约

    字段对照：
    ┌──────────────────┬──────────────────────────────────────────┐
    │ 字段             │ UI 来源                                   │
    ├──────────────────┼──────────────────────────────────────────┤
    │ user             │ _13 预约人（登录用户）                       │
    │ spot             │ _13 楼层地图选择 "B13"                      │
    │ date             │ _13 日历选择的日期                          │
    │ start_time       │ _13 时间段选择 "10:00 AM"                  │
    │ end_time         │ _13 起始时间 + 最低2小时                    │
    │ total_amount     │ _13 预约汇总 "总计 $15.00"                 │
    │ qr_code          │ _13 确认弹窗的二维码图片                     │
    │ booking_code     │ _13 确认弹窗 "编号: SENT-982-A1"           │
    │ status           │ _5 最近预订列表的状态标签                    │
    └──────────────────┴──────────────────────────────────────────┘
    """

    class Status(models.TextChoices):
        PENDING = 'pending', '待确认'
        CONFIRMED = 'confirmed', '已确认'
        COMPLETED = 'completed', '已完成'
        CANCELLED = 'cancelled', '已取消'
        EXPIRED = 'expired', '已过期'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='reservations', verbose_name='预约人'
    )
    spot = models.ForeignKey(
        'ParkingSpace', on_delete=models.CASCADE,
        related_name='reservations', verbose_name='车位'
    )
    date = models.DateField('预约日期')
    end_date = models.DateField('离开日期', null=True, blank=True, help_text='不填时默认与预约日期相同')
    start_time = models.TimeField('开始时间')
    end_time = models.TimeField('结束时间')
    total_amount = models.DecimalField(
        '总费用', max_digits=10, decimal_places=2, default=0,
        help_text='基础费率 + 优选车位附加费 + 预约服务费'
    )
    payment_method = models.CharField('支付方式', max_length=20, blank=True, default='', help_text='预约创建时使用的支付方式')
    payment_transaction_id = models.CharField('支付交易ID', max_length=64, blank=True, default='', help_text='余额支付的交易流水号，用于取消预约时退款')
    booking_code = models.CharField(
        '预约编号', max_length=30, unique=True,
        help_text='如 SENT-982-A1，确认弹窗中展示'
    )
    qr_code = models.ImageField(
        '入场二维码', upload_to='qrcodes/', blank=True, null=True,
        help_text='确认后生成的电子凭证'
    )
    status = models.CharField(
        '预约状态', max_length=12, choices=Status.choices,
        default=Status.PENDING
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '车位预约'
        verbose_name_plural = '车位预约'
        db_table = 'sentinel_reservation'
        ordering = ['-date', '-end_date', '-start_time']

    def __str__(self) -> str:
        return f'{self.booking_code} - {self.spot} ({self.date})'


class SpotConnection(models.Model):
    """
    停车位拓扑连接 — 定义停车场地图中车位之间的导航关系
    用于 Dijkstra 最短路径算法
    
    示例：
    - 从停车位 A-01 到相邻停车位 A-02 的距离是 1.5 米
    - 从停车位 A-12 到通道 CORRIDOR-01 的距离是 2.0 米
    """
    from_spot = models.ForeignKey(
        'ParkingSpace', on_delete=models.CASCADE,
        related_name='outgoing_connections',
        verbose_name='起点车位'
    )
    to_spot = models.ForeignKey(
        'ParkingSpace', on_delete=models.CASCADE,
        related_name='incoming_connections',
        verbose_name='终点车位'
    )
    distance = models.FloatField(
        '路径距离',
        default=1.0,
        help_text='两个车位间的导航距离（单位：米）'
    )
    
    class Meta:
        verbose_name = '停车位连接'
        verbose_name_plural = '停车位连接'
        db_table = 'sentinel_spot_connection'
        unique_together = ('from_spot', 'to_spot')
        indexes = [
            models.Index(fields=['from_spot', 'to_spot']),
        ]
    
    def __str__(self) -> str:
        return f'{self.from_spot.space_id} → {self.to_spot.space_id} ({self.distance}m)'
