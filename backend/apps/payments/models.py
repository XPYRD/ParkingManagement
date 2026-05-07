"""
payments — 支付、订阅、定价规则数据模型

数据来源：
- Payment: _4(支付历史表格) + _9(交易明细日志)
- Subscription: _4(订阅套餐卡片) + _10(用户表格订阅列)
- PricingRule: _9(定价规则配置卡片)
"""

from django.conf import settings
from django.db import models
from decimal import Decimal


class SubscriptionPlan(models.Model):
    """套餐信息表 — 独立维护可售套餐。"""

    class PlanCode(models.TextChoices):
        MONTHLY = 'monthly', '月卡'
        QUARTERLY = 'quarterly', '季卡'
        YEARLY = 'yearly', '年卡'

    code = models.CharField('套餐编码', max_length=20, choices=PlanCode.choices, unique=True)
    name = models.CharField('套餐名称', max_length=50)
    price = models.DecimalField('套餐价格', max_digits=10, decimal_places=2)
    duration_days = models.PositiveIntegerField('有效天数')
    description = models.CharField('套餐描述', max_length=200, blank=True, default='')
    is_active = models.BooleanField('是否上架', default=True)
    is_recommended = models.BooleanField('是否推荐', default=False)
    sort_order = models.PositiveIntegerField('排序', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '订阅套餐'
        verbose_name_plural = '订阅套餐'
        db_table = 'sentinel_subscription_plan'
        ordering = ['sort_order', 'id']

    def __str__(self) -> str:
        return f'{self.name} (¥{self.price})'


class Payment(models.Model):
    """
    支付记录

    字段对照：
    ┌──────────────────┬──────────────────────────────────────────┐
    │ 字段             │ UI 来源                                   │
    ├──────────────────┼──────────────────────────────────────────┤
    │ session          │ _4 支付关联的停车会话                       │
    │ transaction_id   │ _4 支付历史表格 "交易ID" 列                 │
    │ amount           │ _4 "金额" 列 / _9 交易日志"金额"列          │
    │ method           │ _4 支付方式按钮 (微信/支付宝/ETC/信用卡)      │
    │ status           │ _4 历史记录"状态"列 + _9 日志"状态"列        │
    └──────────────────┴──────────────────────────────────────────┘
    """

    class Method(models.TextChoices):
        """支付方式 — _4 支付方式选择区域"""
        WECHAT = 'wechat', '微信支付'
        ALIPAY = 'alipay', '支付宝'
        CARD = 'card', '银行卡'
        BALANCE = 'balance', '余额支付'
        CASH = 'cash', '现金'

    class BizType(models.TextChoices):
        """业务类型 — _9 交易日志"""
        PARKING_FEE = 'parking_fee', '停车缴费'
        SUBSCRIPTION = 'subscription', '套餐订阅'
        RESERVATION = 'reservation', '车位预定'

    class Status(models.TextChoices):
        """支付状态 — _4 历史记录状态标签"""
        SUCCESS = 'success', '成功'
        FAILED = 'failed', '失败'
        REFUNDED = 'refunded', '已退款'
        PENDING = 'pending', '处理中'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='payments', verbose_name='用户'
    )
    session = models.ForeignKey(
        'parking.ParkingSession', on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='payments', verbose_name='关联停车会话'
    )
    transaction_id = models.CharField(
        '交易ID', max_length=64, unique=True,
        help_text='系统生成的唯一交易标识'
    )
    amount = models.DecimalField(
        '金额', max_digits=10, decimal_places=2,
        help_text='单位：元'
    )
    method = models.CharField(
        '支付方式', max_length=10, choices=Method.choices
    )
    status = models.CharField(
        '支付状态', max_length=10, choices=Status.choices,
        default=Status.PENDING
    )
    biz_type = models.CharField(
        '业务类型', max_length=20, choices=BizType.choices,
        default=BizType.PARKING_FEE,
        help_text='交易日志的业务分类'
    )
    remark = models.CharField(
        '备注', max_length=200, blank=True, default='',
        help_text='交易说明或失败原因'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '支付记录'
        verbose_name_plural = '支付记录'
        db_table = 'sentinel_payment'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.transaction_id} ¥{self.amount} ({self.get_status_display()})'


class Subscription(models.Model):
    """
    订阅套餐

    字段对照：
    ┌──────────────────┬──────────────────────────────────────────┐
    │ 字段             │ UI 来源                                   │
    ├──────────────────┼──────────────────────────────────────────┤
    │ plan             │ _4 套餐卡片标题 (月卡/年卡)                 │
    │ price            │ _4 套餐卡片价格 (¥149/月, ¥1299/年)        │
    │ start_date       │ 激活日期                                   │
    │ end_date         │ 到期日期                                   │
    │ is_active        │ _10 用户表格"订阅"列的激活标签              │
    └──────────────────┴──────────────────────────────────────────┘
    """

    class Plan(models.TextChoices):
        """套餐类型 — _4 订阅卡片"""
        MONTHLY = 'monthly', '月卡'
        QUARTERLY = 'quarterly', '季卡'
        YEARLY = 'yearly', '年卡'
        BASIC = 'basic', '基础版'
        ADVANCED = 'advanced', '高级版'
        ELITE = 'elite', '尊享版'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='subscriptions', verbose_name='用户'
    )
    plan_ref = models.ForeignKey(
        'payments.SubscriptionPlan', on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='subscriptions', verbose_name='套餐信息'
    )
    plan = models.CharField(
        '套餐类型', max_length=10, choices=Plan.choices
    )
    price = models.DecimalField(
        '价格', max_digits=10, decimal_places=2,
        help_text='单位：元'
    )
    start_date = models.DateField('开始日期')
    end_date = models.DateField('结束日期')
    is_active = models.BooleanField(
        '是否生效', default=True,
        help_text='到期或手动取消后置为 False'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '订阅计划'
        verbose_name_plural = '订阅计划'
        db_table = 'sentinel_subscription'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.user} - {self.get_plan_display()} ({self.start_date} ~ {self.end_date})'


class PricingRule(models.Model):
    """
    定价规则 — 管理后台可配置

    字段对照（来自 _9 收费管理页面的定价规则卡片）：
    ┌──────────────────┬──────────────────────────────────────────┐
    │ 字段             │ UI 来源                                   │
    ├──────────────────┼──────────────────────────────────────────┤
    │ rate_type        │ _9 规则卡片标题 (标准时段/高峰时段/...)      │
    │ value            │ _9 输入框中的费率数值                       │
    │ unit             │ _9 规则说明 "元/小时" / "分钟" / "元/月"    │
    │ description      │ _9 规则卡片副标题说明                       │
    │ is_active        │ 是否启用此规则                              │
    └──────────────────┴──────────────────────────────────────────┘
    """

    class RateType(models.TextChoices):
        HOURLY_STANDARD = 'hourly_standard', '标准时段（元/小时）'
        HOURLY_PEAK = 'hourly_peak', '高峰时段（元/小时）'
        HOURLY_FIRST = 'hourly_first', '首小时费率（元/小时）'
        HOURLY_SUBSEQUENT = 'hourly_subsequent', '后续每小时（元/小时）'
        HOURLY_SWITCH_HOUR = 'hourly_switch_hour', '切换日租起始小时数'
        DAILY_RATE = 'daily_rate', '日租价（元/天）'
        DAILY_CAP = 'daily_cap', '单日封顶（元/天）'
        RESERVATION_DAILY = 'reservation_daily', '预约基础费（元/天）'
        RESERVATION_EV_SURCHARGE = 'reservation_ev_surcharge', '预约充电桩附加费（元/单）'
        GRACE_ENTRY = 'grace_entry', '入场宽限期（分钟）'
        GRACE_EXIT = 'grace_exit', '出场宽限期（分钟）'
        MONTHLY_COMMUTE = 'monthly_commute', '月卡-通勤版'
        MONTHLY_PREMIUM = 'monthly_premium', '月卡-高级版'

    rate_type = models.CharField(
        '费率类型', max_length=32, choices=RateType.choices, unique=True
    )
    value = models.DecimalField(
        '数值', max_digits=10, decimal_places=2,
        help_text='费率值或时长值'
    )
    unit = models.CharField(
        '单位', max_length=20,
        help_text='元/小时、分钟、元/月 等'
    )
    description = models.CharField(
        '规则说明', max_length=200, blank=True, default='',
        help_text='管理后台卡片中的副标题'
    )
    is_active = models.BooleanField('是否启用', default=True)
    effective_date = models.DateField(
        '生效日期',
        help_text='该规则从何时开始生效'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '定价规则'
        verbose_name_plural = '定价规则'
        db_table = 'sentinel_pricing_rule'
        ordering = ['rate_type']

    def __str__(self) -> str:
        return f'{self.get_rate_type_display()}: {self.value} {self.unit}'

    @classmethod
    def get_active_value(cls, rate_type: str, default: Decimal | None = None) -> Decimal | None:
        rule = cls.objects.filter(rate_type=rate_type, is_active=True).order_by('-effective_date', '-updated_at').first()
        if rule is None:
            return default
        return rule.value

    @classmethod
    def calculate_parking_fee(cls, total_minutes: int) -> tuple:
        """
        计算停车费

        计费逻辑：
        1. 不足1小时按1小时计（至少收首小时费）
        2. 首小时：按 HOURLY_FIRST（默认 ¥6）
        3. 后续每小时：按 HOURLY_SUBSEQUENT（默认 ¥4），直到达到 HOURLY_SWITCH_HOUR（默认 5 小时）
        4. 超过切换小时后：按 DAILY_RATE（默认 ¥30/天）计费
        5. 每日不超过 DAILY_CAP（默认 ¥60）

        返回: (amount, chargeable_hours)
        """
        from decimal import Decimal, ROUND_HALF_UP

        # 至少1小时
        if total_minutes <= 0:
            total_minutes = 1

        hourly_first = cls.get_active_value(cls.RateType.HOURLY_FIRST, Decimal('6.00'))
        hourly_subsequent = cls.get_active_value(cls.RateType.HOURLY_SUBSEQUENT, Decimal('4.00'))
        switch_hour = cls.get_active_value(cls.RateType.HOURLY_SWITCH_HOUR, Decimal('5'))
        daily_rate = cls.get_active_value(cls.RateType.DAILY_RATE, Decimal('30.00'))
        daily_cap = cls.get_active_value(cls.RateType.DAILY_CAP, Decimal('60.00'))

        switch_hour = int(switch_hour)
        total_full_days = total_minutes // (24 * 60)
        remaining_minutes = total_minutes % (24 * 60)

        amount = Decimal('0')

        if total_full_days > 0:
            amount += total_full_days * min(daily_rate, daily_cap)

        # 计算剩余不足一天的部分
        if remaining_minutes > 0:
            remaining_hours = remaining_minutes // 60
            remaining_mins = remaining_minutes % 60
            chargeable_remaining = remaining_hours + (1 if remaining_mins > 0 else 0)

            if chargeable_remaining <= 1:
                amount += hourly_first * chargeable_remaining
            elif chargeable_remaining <= switch_hour:
                amount += hourly_first + hourly_subsequent * (chargeable_remaining - 1)
            else:
                # 剩余部分超过切换小时，按日租算
                amount += min(daily_rate, daily_cap)

        amount = amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        # 计费小时数
        chargeable_hours = max(1, total_minutes // 60 + (1 if total_minutes % 60 > 0 else 0))

        return amount, chargeable_hours


class BankCard(models.Model):
    """用户银行卡 — 用于支付方式选择。"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='bank_cards', verbose_name='用户'
    )
    bank_name = models.CharField('银行名称', max_length=50)
    card_type = models.CharField('卡类型', max_length=20, blank=True, default='')
    holder_name = models.CharField('持卡人姓名', max_length=50)
    card_last4 = models.CharField('卡号后4位', max_length=4)
    bin_prefix = models.CharField('BIN前缀', max_length=8, blank=True, default='')
    is_default = models.BooleanField('是否默认卡', default=True)
    is_active = models.BooleanField('是否有效', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '银行卡'
        verbose_name_plural = '银行卡'
        db_table = 'sentinel_bank_card'
        ordering = ['-is_default', '-updated_at', '-id']

    def __str__(self) -> str:
        return f'{self.holder_name} — {self.bank_name} (*{self.card_last4})'


class UserBalance(models.Model):
    """
    用户余额管理 — 支持充值、扣费、查询
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='balance', verbose_name='用户'
    )
    balance = models.DecimalField(
        '账户余额', max_digits=10, decimal_places=2,
        default=0, help_text='单位：元'
    )
    total_recharged = models.DecimalField(
        '累计充值', max_digits=10, decimal_places=2,
        default=0, help_text='历史累计充值总额'
    )
    total_consumed = models.DecimalField(
        '累计消费', max_digits=10, decimal_places=2,
        default=0, help_text='历史累计消费总额'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '用户余额'
        verbose_name_plural = '用户余额'
        db_table = 'sentinel_user_balance'

    def __str__(self) -> str:
        return f'{self.user} - ¥{self.balance}'


class TopUpRecord(models.Model):
    """
    充值记录 — 记录所有充值交易
    """
    class Status(models.TextChoices):
        """充值状态"""
        SUCCESS = 'success', '成功'
        PENDING = 'pending', '处理中'
        FAILED = 'failed', '失败'
        CANCELLED = 'cancelled', '已取消'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='topups', verbose_name='用户'
    )
    transaction_id = models.CharField(
        '交易ID', max_length=64, unique=True,
        help_text='系统生成的唯一交易标识'
    )
    amount = models.DecimalField(
        '充值金额', max_digits=10, decimal_places=2,
        help_text='单位：元'
    )
    payment_method = models.CharField(
        '支付方式', max_length=10,
        choices=[
            ('wechat', '微信支付'),
            ('alipay', '支付宝'),
            ('card', '银行卡'),
        ]
    )
    status = models.CharField(
        '充值状态', max_length=10, choices=Status.choices,
        default=Status.PENDING
    )
    remark = models.CharField(
        '备注', max_length=200, blank=True, default=''
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '充值记录'
        verbose_name_plural = '充值记录'
        db_table = 'sentinel_topup_record'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.user} - ¥{self.amount} ({self.get_status_display()})'
