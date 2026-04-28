"""
devices — 设备管理数据模型

数据来源：_11(设备管理页面) 设备卡片 + 统计指标 + 动态日志
"""

from django.db import models


class Device(models.Model):
    """
    停车场硬件设备

    字段对照（来自 _11 设备管理页面）：
    ┌──────────────────┬──────────────────────────────────────────┐
    │ 字段             │ UI 来源                                   │
    ├──────────────────┼──────────────────────────────────────────┤
    │ name             │ 设备卡片标题 "道闸 1" / "入口摄像头 2"       │
    │ device_type      │ 卡片图标类型 (道闸/摄像头/自助终端/传感器)    │
    │ location         │ 卡片副标题 "北入口 - A车道"                 │
    │ serial_number    │ 卡片详情 "序列号: SB-001-N"                │
    │ status           │ 卡片状态标签 (在线 🟢 / 故障 🔴)            │
    │ uptime           │ 卡片详情 "正常运行时间: 99.8%"             │
    │ last_maintenance │ 卡片详情 "上次维护: 2023年10月12日"         │
    │ fault_detail     │ 故障卡片 "问题: 信号丢失"                  │
    │ offline_since    │ 故障卡片 "离线时长: 42分钟前"               │
    └──────────────────┴──────────────────────────────────────────┘
    """

    class DeviceType(models.TextChoices):
        """设备类型 — _11 设备卡片图标"""
        GATE = 'gate', '道闸'
        CAMERA = 'camera', '摄像头'
        KIOSK = 'kiosk', '自助终端'
        SENSOR = 'sensor', '传感器'

    class Status(models.TextChoices):
        """设备状态 — _11 卡片状态标签"""
        ONLINE = 'online', '在线'
        OFFLINE = 'offline', '离线'
        ERROR = 'error', '故障'
        MAINTENANCE = 'maintenance', '维护中'

    name = models.CharField(
        '设备名称', max_length=50,
        help_text='如：道闸 1, 入口摄像头 2'
    )
    device_type = models.CharField(
        '设备类型', max_length=15, choices=DeviceType.choices
    )
    location = models.CharField(
        '安装位置', max_length=100,
        help_text='如：北入口 - A车道, 1层 - 主电梯大堂'
    )
    serial_number = models.CharField(
        '序列号', max_length=50, unique=True,
        help_text='如：SB-001-N, KS-442-LV1'
    )
    status = models.CharField(
        '运行状态', max_length=15, choices=Status.choices,
        default=Status.ONLINE
    )
    uptime = models.DecimalField(
        '正常运行率', max_digits=5, decimal_places=2, default=100.00,
        help_text='百分比，如 99.80 表示 99.8%'
    )
    last_maintenance = models.DateField(
        '上次维护日期', null=True, blank=True
    )
    fault_detail = models.CharField(
        '故障说明', max_length=200, blank=True, default='',
        help_text='故障卡片中的 "问题" 字段'
    )
    offline_since = models.DateTimeField(
        '离线起始时间', null=True, blank=True,
        help_text='故障卡片中的 "离线时长" 推算'
    )
    # 自助终端特有属性
    paper_level = models.IntegerField(
        '纸张余量', null=True, blank=True,
        help_text='自助终端纸张余量百分比，如 22'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '设备'
        verbose_name_plural = '设备'
        db_table = 'sentinel_device'
        ordering = ['device_type', 'name']

    def __str__(self) -> str:
        return f'{self.name} ({self.get_device_type_display()}) [{self.get_status_display()}]'
