"""
alerts — 预警与工单数据模型

数据来源：
- Alert: _7(后台首页告警表格) + center(预警中心告警Feed)
- Ticket: _12(故障/投诉反馈页面工单列表)
"""

from django.conf import settings
from django.db import models


class Alert(models.Model):
    """
    系统预警/告警

    字段对照：
    ┌──────────────────┬──────────────────────────────────────────┐
    │ 字段             │ UI 来源                                   │
    ├──────────────────┼──────────────────────────────────────────┤
    │ alert_type       │ center 告警Feed图标分类 + _7 表格"类型"列   │
    │ title            │ center Feed标题 "设备离线: B区摄像头#4"     │
    │ detail           │ center Feed描述文本                        │
    │ location         │ center Feed "位置" / _7 表格"区域"列        │
    │ severity         │ center 统计卡级别 (紧急/待处理/已调查)       │
    │ status           │ center Feed状态标签 / _7 表格"处理状态"列    │
    └──────────────────┴──────────────────────────────────────────┘
    """

    class AlertType(models.TextChoices):
        """告警类型 — center 预警Feed图标分类"""
        OVERSTAY = 'overstay', '超时停放'
        SECURITY = 'security', '安全事件'
        PAYMENT = 'payment', '支付异常'
        DEVICE = 'device', '设备故障'
        SYSTEM = 'system', '系统告警'

    class Severity(models.TextChoices):
        """严重程度 — center 统计卡颜色等级"""
        EMERGENCY = 'emergency', '紧急'
        WARNING = 'warning', '警告'
        INFO = 'info', '提示'

    class Status(models.TextChoices):
        """处理状态 — center Feed状态标签"""
        PENDING = 'pending', '待处理'
        INVESTIGATING = 'investigating', '调查中'
        RESOLVED = 'resolved', '已解决'
        DISMISSED = 'dismissed', '已忽略'

    alert_type = models.CharField(
        '告警类型', max_length=12, choices=AlertType.choices
    )
    title = models.CharField(
        '告警标题', max_length=100,
        help_text='如：设备离线: B区摄像头#4'
    )
    detail = models.TextField(
        '详细描述', blank=True, default='',
        help_text='Feed 描述文本'
    )
    location = models.CharField(
        '位置', max_length=100, blank=True, default='',
        help_text='如：B2层-A区, 南出口'
    )
    severity = models.CharField(
        '严重程度', max_length=12, choices=Severity.choices,
        default=Severity.INFO
    )
    status = models.CharField(
        '处理状态', max_length=15, choices=Status.choices,
        default=Status.PENDING
    )
    resolved_at = models.DateTimeField(
        '解决时间', null=True, blank=True
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '系统预警'
        verbose_name_plural = '系统预警'
        db_table = 'sentinel_alert'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'[{self.get_severity_display()}] {self.title}'


class Ticket(models.Model):
    """
    用户工单（故障报告/投诉/建议）

    字段对照（来自 _12 故障/投诉反馈页面）：
    ┌──────────────────┬──────────────────────────────────────────┐
    │ 字段             │ UI 来源                                   │
    ├──────────────────┼──────────────────────────────────────────┤
    │ ticket_id        │ 工单卡片 "#ST-9921"                       │
    │ ticket_type      │ 反馈表单 "反馈类型" 下拉框                  │
    │ title            │ 工单卡片标题 "设备故障：4层传感器"            │
    │ description      │ 反馈表单 "详细描述" 文本域                  │
    │ attachments      │ 反馈表单 "证明材料" 上传区域                 │
    │ status           │ 工单卡片状态标签 (已提交/审核中/已解决)       │
    └──────────────────┴──────────────────────────────────────────┘
    """

    class TicketType(models.TextChoices):
        """工单类型 — _12 反馈类型下拉框"""
        DEVICE_FAULT = 'device_fault', '设备故障'
        COMPLAINT = 'complaint', '服务投诉'
        SUGGESTION = 'suggestion', '改进建议'

    class Status(models.TextChoices):
        """工单状态 — _12 工单卡片标签"""
        SUBMITTED = 'submitted', '已提交'
        REVIEWING = 'reviewing', '审核中'
        RESOLVED = 'resolved', '已解决'
        CLOSED = 'closed', '已关闭'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='tickets', verbose_name='提交人'
    )
    ticket_id = models.CharField(
        '工单编号', max_length=20, unique=True,
        help_text='格式如 #ST-9921，系统自动生成'
    )
    ticket_type = models.CharField(
        '反馈类型', max_length=15, choices=TicketType.choices
    )
    title = models.CharField(
        '标题', max_length=100,
        help_text='如：设备故障：4层传感器'
    )
    description = models.TextField(
        '详细描述',
        help_text='反馈表单中的文本域内容'
    )
    attachment = models.ImageField(
        '附件', upload_to='tickets/', blank=True, null=True,
        help_text='证明材料照片或截图'
    )
    status = models.CharField(
        '工单状态', max_length=12, choices=Status.choices,
        default=Status.SUBMITTED
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '用户工单'
        verbose_name_plural = '用户工单'
        db_table = 'sentinel_ticket'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.ticket_id} - {self.title} [{self.get_status_display()}]'
