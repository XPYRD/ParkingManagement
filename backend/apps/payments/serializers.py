"""
payments — 序列化器

前后端字段对齐：
- Payment → _4 支付历史表格 + _9 交易明细
- Subscription → _4 订阅套餐卡片
- PricingRule → _9 定价规则配置
"""

from rest_framework import serializers
from .models import BankCard, Payment, Subscription, SubscriptionPlan, PricingRule, UserBalance, TopUpRecord


class PaymentSerializer(serializers.ModelSerializer):
    """
    支付记录 — 对应 _4 支付历史 + _9 交易明细

    表格列 → 字段映射：
    - 交易ID → transaction_id
    - 金额 → amount
    - 支付方式 → method / method_label
    - 状态 → status / status_label
    - 时间 → created_at
    """

    method_label = serializers.CharField(
        source='get_method_display', read_only=True
    )
    status_label = serializers.CharField(
        source='get_status_display', read_only=True
    )
    # 关联的车牌号 — 表格中需要展示
    plate_number = serializers.CharField(
        source='session.vehicle.plate_number',
        read_only=True, default=''
    )
    biz_type_label = serializers.CharField(
        source='get_biz_type_display', read_only=True
    )
    # 向后兼容：payment_type 从 biz_type 映射
    payment_type = serializers.SerializerMethodField()
    payment_type_label = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'session', 'transaction_id',
            'amount', 'method', 'method_label',
            'status', 'status_label', 'biz_type', 'biz_type_label',
            'payment_type', 'payment_type_label',
            'plate_number', 'remark', 'created_at',
        ]
        read_only_fields = ['id', 'user', 'transaction_id', 'created_at']

    BIZ_TYPE_MAP = {
        'parking_fee': 'parking',
        'subscription': 'subscription',
        'reservation': 'reservation',
    }
    BIZ_TYPE_LABEL_MAP = {
        'parking_fee': '停车缴费',
        'subscription': '套餐订阅',
        'reservation': '车位预定',
    }

    def get_payment_type(self, obj):
        return self.BIZ_TYPE_MAP.get(obj.biz_type, 'other')

    def get_payment_type_label(self, obj):
        return self.BIZ_TYPE_LABEL_MAP.get(obj.biz_type, '其他支付')


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    订阅套餐 — 对应 _4 套餐卡片

    卡片字段 → 映射：
    - 标题 → plan_label
    - 价格 → price
    - 状态 → is_active
    """

    plan_label = serializers.CharField(
        source='get_plan_display', read_only=True
    )
    username = serializers.CharField(
        source='user.username', read_only=True
    )
    plan_ref_id = serializers.IntegerField(source='plan_ref.id', read_only=True)
    plan_name = serializers.CharField(source='plan_ref.name', read_only=True, default='')
    plan_duration_days = serializers.IntegerField(source='plan_ref.duration_days', read_only=True, default=0)

    class Meta:
        model = Subscription
        fields = [
            'id', 'user', 'username', 'plan', 'plan_label',
            'plan_ref_id', 'plan_name', 'plan_duration_days',
            'price', 'start_date', 'end_date',
            'is_active', 'created_at',
        ]
        read_only_fields = [
            'id', 'user', 'username',
            'plan_ref_id', 'plan_name', 'plan_duration_days',
            'plan_label', 'created_at',
        ]


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    """套餐信息表序列化。"""

    code_label = serializers.CharField(source='get_code_display', read_only=True)

    class Meta:
        model = SubscriptionPlan
        fields = [
            'id', 'code', 'code_label', 'name',
            'price', 'duration_days', 'description',
            'is_active', 'is_recommended', 'sort_order',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PricingRuleSerializer(serializers.ModelSerializer):
    """
    定价规则 — 对应 _9 定价配置区域

    配置卡片字段 → 映射：
    - 规则名称 → rate_type_label
    - 值 / 输入框 → value
    - 单位 → unit
    - 说明 → description
    """

    rate_type_label = serializers.CharField(
        source='get_rate_type_display', read_only=True
    )

    class Meta:
        model = PricingRule
        fields = [
            'id', 'rate_type', 'rate_type_label',
            'value', 'unit', 'description',
            'is_active', 'effective_date',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserBalanceSerializer(serializers.ModelSerializer):
    """用户余额 — 账户余额、充值、消费统计"""
    
    username = serializers.CharField(
        source='user.username', read_only=True
    )

    class Meta:
        model = UserBalance
        fields = [
            'id', 'user', 'username', 'balance',
            'total_recharged', 'total_consumed',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user', 'total_recharged', 'total_consumed', 'created_at', 'updated_at']


class BankCardSerializer(serializers.ModelSerializer):
    """银行卡 — 用户支付方式绑定。"""

    class Meta:
        model = BankCard
        fields = [
            'id', 'user', 'bank_name', 'card_type',
            'holder_name', 'card_last4', 'bin_prefix',
            'is_default', 'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class TopUpRecordSerializer(serializers.ModelSerializer):
    """充值记录 — 用户充值交易历史"""
    
    username = serializers.CharField(
        source='user.username', read_only=True
    )
    payment_method_label = serializers.CharField(
        source='get_payment_method_display', read_only=True
    )
    status_label = serializers.CharField(
        source='get_status_display', read_only=True
    )
    payment_type = serializers.SerializerMethodField()
    payment_type_label = serializers.SerializerMethodField()
    method = serializers.CharField(source='payment_method', read_only=True)
    method_label = serializers.CharField(source='get_payment_method_display', read_only=True)

    class Meta:
        model = TopUpRecord
        fields = [
            'id', 'user', 'username', 'transaction_id',
            'amount', 'payment_method', 'payment_method_label',
            'method', 'method_label',
            'payment_type', 'payment_type_label',
            'status', 'status_label', 'remark',
            'created_at',
        ]
        read_only_fields = ['id', 'user', 'transaction_id', 'created_at']

    def get_payment_type(self, obj):
        return 'topup'

    def get_payment_type_label(self, obj):
        return '余额充值'
