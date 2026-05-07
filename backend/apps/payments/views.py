"""
payments — API 视图

端点清单：
- GET    /api/v1/payments/records/                 支付记录列表
- GET    /api/v1/payments/records/{id}/            支付详情
- GET    /api/v1/payments/records/summary/         营收汇总统计
- GET    /api/v1/payments/subscriptions/           订阅列表
- POST   /api/v1/payments/subscriptions/           创建订阅
- GET    /api/v1/payments/rules/                   定价规则列表
- PUT    /api/v1/payments/rules/{id}/              [管理端] 更新规则
"""

import time
from decimal import Decimal, InvalidOperation
from urllib.parse import quote_plus
from django.db import transaction
from django.db.models import Sum, Count, Avg
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import BankCard, Payment, Subscription, SubscriptionPlan, PricingRule, UserBalance, TopUpRecord
from .serializers import (
    BankCardSerializer,
    PaymentSerializer,
    SubscriptionSerializer,
    SubscriptionPlanSerializer,
    PricingRuleSerializer,
    UserBalanceSerializer,
    TopUpRecordSerializer,
)


class PaymentViewSet(viewsets.ModelViewSet):
    """
    支付记录 — 对应 _4 支付历史 + _9 交易明细

    用户端：查看自己的支付记录
    管理端：查看所有记录 + 营收统计
    """
    serializer_class = PaymentSerializer
    filterset_fields = ['method', 'status']
    search_fields = ['transaction_id']
    ordering_fields = ['created_at', 'amount']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(user=user)

    @staticmethod
    def _build_sandbox_qr(transaction_id, amount, method, biz_type='parking_pay'):
        payload = f"SANDBOX|{biz_type}|{transaction_id}|{amount}|{method}"
        return f"https://api.qrserver.com/v1/create-qr-code/?size=260x260&data={quote_plus(payload)}"

    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request):
        """
        营收汇总 — 对应 _9 顶部统计卡

        GET /api/v1/payments/records/summary/
        返回：{total_revenue, total_count, avg_amount, method_breakdown}

        对应的 _9 页面元素：
        - 总营收 ¥142,850 → total_revenue
        - 平均客单价 ¥14.20 → avg_amount
        - 支付类型占比 → method_breakdown
        """
        if not request.user.is_staff:
            return Response({'detail': '仅管理员可访问'}, status=403)

        valid_biz_types = [
            Payment.BizType.PARKING_FEE,
            Payment.BizType.SUBSCRIPTION,
            Payment.BizType.RESERVATION,
        ]
        qs = Payment.objects.filter(
            status=Payment.Status.SUCCESS,
            biz_type__in=valid_biz_types,
        )
        stats = qs.aggregate(
            total_revenue=Sum('amount'),
            total_count=Count('id'),
            avg_amount=Avg('amount'),
        )
        # 将 Decimal 转为 float，前端 .toFixed() 需要数值类型
        if stats.get('total_revenue') is not None:
            stats['total_revenue'] = float(stats['total_revenue'])
        if stats.get('avg_amount') is not None:
            stats['avg_amount'] = float(stats['avg_amount'])
        # 按支付方式统计占比 — 对应 _9 "支付类型占比" 饼图
        method_breakdown = list(
            qs.values('method').annotate(
                count=Count('id'),
                total=Sum('amount'),
            ).order_by('-total')
        )
        for item in method_breakdown:
            if item.get('total') is not None:
                item['total'] = float(item['total'])
        stats['method_breakdown'] = method_breakdown
        return Response(stats)

    @action(detail=False, methods=['post'], url_path='sandbox-create')
    def sandbox_create(self, request):
        """创建沙箱停车支付订单，返回二维码和待支付状态。"""
        amount_raw = request.data.get('amount')
        method = request.data.get('method')
        session_id = request.data.get('session_id')
        remark = request.data.get('remark', '停车费支付')

        try:
            amount = Decimal(str(amount_raw))
        except (InvalidOperation, TypeError, ValueError):
            return Response({'detail': '支付金额格式错误'}, status=400)

        if amount <= 0:
            return Response({'detail': '支付金额必须大于0'}, status=400)

        if method not in {Payment.Method.WECHAT, Payment.Method.ALIPAY, Payment.Method.CARD}:
            return Response({'detail': '该支付方式不支持沙箱扫码'}, status=400)

        transaction_id = f"PAYSBX_{request.user.id}_{int(time.time() * 1000)}"
        payment = Payment.objects.create(
            user=request.user,
            transaction_id=transaction_id,
            amount=amount,
            method=method,
            status=Payment.Status.PENDING,
            biz_type=Payment.BizType.PARKING_FEE,
            remark=remark,
            session_id=session_id if session_id else None,
        )
        qr_code_url = self._build_sandbox_qr(transaction_id, amount, method)

        return Response({
            'mode': 'sandbox',
            'payment_id': payment.id,
            'transaction_id': transaction_id,
            'amount': f"{amount:.2f}",
            'method': method,
            'status': payment.status,
            'expires_in_seconds': 300,
            'qr_code_url': qr_code_url,
            'display_payload': f"{transaction_id}|¥{amount:.2f}|{method}",
        }, status=201)

    @action(detail=False, methods=['post'], url_path='sandbox-confirm')
    def sandbox_confirm(self, request):
        """确认沙箱停车支付订单（模拟用户扫码后支付成功）。"""
        transaction_id = request.data.get('transaction_id')
        success = bool(request.data.get('success', True))

        if not transaction_id:
            return Response({'detail': 'transaction_id 不能为空'}, status=400)

        payment = Payment.objects.filter(
            user=request.user,
            transaction_id=transaction_id,
        ).first()
        if not payment:
            return Response({'detail': '未找到支付订单'}, status=404)

        if payment.status == Payment.Status.SUCCESS:
            return Response({'detail': '订单已支付', 'status': payment.status})

        payment.status = Payment.Status.SUCCESS if success else Payment.Status.FAILED
        payment.save(update_fields=['status'])
        return Response({'detail': '支付状态已更新', 'status': payment.status})


class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    订阅管理 — 对应 _4 订阅套餐

    用户端：查看和购买自己的订阅
    管理端：查看所有订阅
    """
    serializer_class = SubscriptionSerializer
    filterset_fields = ['plan', 'is_active']
    ordering_fields = ['created_at', 'end_date']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Subscription.objects.all()
        return Subscription.objects.filter(user=user)

    def perform_create(self, serializer):
        """创建订阅时自动关联当前用户，并记录 Payment"""
        plan_ref_id = self.request.data.get('plan_ref_id')
        plan_ref = None
        if plan_ref_id:
            plan_ref = SubscriptionPlan.objects.filter(id=plan_ref_id, is_active=True).first()
            if plan_ref:
                sub = serializer.save(
                    user=self.request.user,
                    plan_ref=plan_ref,
                    plan=plan_ref.code,
                    price=plan_ref.price,
                )
                Payment.objects.create(
                    user=self.request.user,
                    transaction_id=f"SUB_{self.request.user.id}_{int(time.time() * 1000)}",
                    amount=plan_ref.price,
                    method=self.request.data.get('payment_method', Payment.Method.BALANCE),
                    status=Payment.Status.SUCCESS,
                    biz_type=Payment.BizType.SUBSCRIPTION,
                    remark=f'套餐订阅 {plan_ref.name}',
                )
                return

        plan_code = self.request.data.get('plan')
        plan_ref = SubscriptionPlan.objects.filter(code=plan_code, is_active=True).first()
        if plan_ref:
            sub = serializer.save(
                user=self.request.user,
                plan_ref=plan_ref,
                plan=plan_ref.code,
                price=plan_ref.price,
            )
            Payment.objects.create(
                user=self.request.user,
                transaction_id=f"SUB_{self.request.user.id}_{int(time.time() * 1000)}",
                amount=plan_ref.price,
                method=self.request.data.get('payment_method', Payment.Method.BALANCE),
                status=Payment.Status.SUCCESS,
                biz_type=Payment.BizType.SUBSCRIPTION,
                remark=f'套餐订阅 {plan_ref.name}',
            )
            return

        serializer.save(user=self.request.user)


class SubscriptionPlanViewSet(viewsets.ModelViewSet):
    """套餐信息表：用户可读，管理员可维护。"""

    serializer_class = SubscriptionPlanSerializer
    queryset = SubscriptionPlan.objects.all()
    filterset_fields = ['code', 'is_active']
    ordering_fields = ['sort_order', 'price', 'duration_days', 'created_at']

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]


class PricingRuleViewSet(viewsets.ModelViewSet):
    """
    定价规则 — 对应 _9 定价规则配置

    所有人可读（前端计算预估费用需要），仅管理员可写
    """
    serializer_class = PricingRuleSerializer
    queryset = PricingRule.objects.all()
    filterset_fields = ['rate_type', 'is_active']

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


class UserBalanceViewSet(viewsets.ViewSet):
    """
    用户余额管理 — 查询和管理个人账户余额
    
    端点：
    - GET    /api/v1/payments/balance/              获取当前用户余额
    - POST   /api/v1/payments/balance/topup/        充值余额
    - POST   /api/v1/payments/balance/pay/          使用余额支付
    - POST   /api/v1/payments/balance/refund/       余额支付退款补偿
    """
    permission_classes = [permissions.IsAuthenticated]

    @staticmethod
    def _parse_positive_amount(raw_amount):
        """将请求金额安全转换为 Decimal，并校验 > 0。"""
        try:
            amount = Decimal(str(raw_amount))
        except (InvalidOperation, TypeError, ValueError):
            return None
        if amount <= 0:
            return None
        return amount

    @staticmethod
    def _build_sandbox_qr(transaction_id, amount, method, biz_type='balance_topup'):
        payload = f"SANDBOX|{biz_type}|{transaction_id}|{amount}|{method}"
        return f"https://api.qrserver.com/v1/create-qr-code/?size=260x260&data={quote_plus(payload)}"

    def list(self, request):
        """获取当前用户的账户余额"""
        try:
            balance_obj = request.user.balance
        except UserBalance.DoesNotExist:
            # 如果不存在，自动创建
            balance_obj = UserBalance.objects.create(user=request.user)
        
        serializer = UserBalanceSerializer(balance_obj)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def topup(self, request):
        """
        充值余额
        
        POST /api/v1/payments/balance/topup/
        {
            "amount": 100.00,
            "payment_method": "wechat"  # wechat, alipay, card
        }
        """
        amount = self._parse_positive_amount(request.data.get('amount'))
        payment_method = request.data.get('payment_method')

        if amount is None:
            return Response({'detail': '充值金额必须大于0'}, status=400)

        allowed_methods = {'wechat', 'alipay', 'card'}
        if payment_method not in allowed_methods:
            return Response({'detail': '不支持的充值方式'}, status=400)

        # 创建充值记录（先置为待支付）
        topup_id = f"TOPUP_{request.user.id}_{int(time.time() * 1000)}"
        topup = TopUpRecord.objects.create(
            user=request.user,
            transaction_id=topup_id,
            amount=amount,
            payment_method=payment_method,
            status=TopUpRecord.Status.PENDING
        )
        qr_code_url = self._build_sandbox_qr(topup_id, amount, payment_method)

        return Response({
            'mode': 'sandbox',
            'transaction_id': topup_id,
            'amount': f"{amount:.2f}",
            'payment_method': payment_method,
            'status': TopUpRecord.Status.PENDING,
            'expires_in_seconds': 300,
            'qr_code_url': qr_code_url,
            'display_payload': f"{topup_id}|¥{amount:.2f}|{payment_method}",
        }, status=201)

    @action(detail=False, methods=['post'], url_path='topup-confirm')
    def topup_confirm(self, request):
        """确认沙箱充值订单（模拟扫码成功后入账）。"""
        transaction_id = request.data.get('transaction_id')
        success = bool(request.data.get('success', True))

        if not transaction_id:
            return Response({'detail': 'transaction_id 不能为空'}, status=400)

        topup = TopUpRecord.objects.filter(
            user=request.user,
            transaction_id=transaction_id,
        ).first()
        if not topup:
            return Response({'detail': '未找到充值订单'}, status=404)

        # 幂等：已成功订单直接返回，避免重复入账
        if topup.status == TopUpRecord.Status.SUCCESS:
            balance_obj, _ = UserBalance.objects.get_or_create(user=request.user)
            return Response({
                'detail': '订单已入账',
                'status': topup.status,
                'balance': f"{balance_obj.balance:.2f}",
            })

        topup.status = TopUpRecord.Status.SUCCESS if success else TopUpRecord.Status.FAILED
        topup.save(update_fields=['status'])

        if topup.status == TopUpRecord.Status.SUCCESS:
            balance_obj, _ = UserBalance.objects.get_or_create(user=request.user)
            balance_obj.balance += topup.amount
            balance_obj.total_recharged += topup.amount
            balance_obj.save(update_fields=['balance', 'total_recharged', 'updated_at'])
            return Response({
                'detail': '充值成功',
                'status': topup.status,
                'amount': f"{topup.amount:.2f}",
                'balance': f"{balance_obj.balance:.2f}",
            })

        return Response({'detail': '充值失败', 'status': topup.status})

    @action(detail=False, methods=['post'])
    def pay(self, request):
        """
        使用余额支付
        
        POST /api/v1/payments/balance/pay/
        {
            "amount": 35.00,
            "session_id": 123,  # 关联的停车会话
            "remark": "停车费"
        }
        """
        amount = self._parse_positive_amount(request.data.get('amount'))
        session_id = request.data.get('session_id')
        remark = request.data.get('remark', '余额支付')

        if amount is None:
            return Response({'detail': '支付金额必须大于0'}, status=400)

        try:
            balance_obj = request.user.balance
        except UserBalance.DoesNotExist:
            return Response({'detail': '账户余额不存在'}, status=400)

        if balance_obj.balance < amount:
            return Response({'detail': '余额不足'}, status=400)

        # 创建支付记录
        payment_id = f"PAY_{request.user.id}_{int(time.time() * 1000)}"
        payment = Payment.objects.create(
            user=request.user,
            transaction_id=payment_id,
            amount=amount,
            method=Payment.Method.BALANCE,
            status=Payment.Status.SUCCESS,
            biz_type=Payment.BizType.PARKING_FEE,
            remark=remark,
            session_id=session_id if session_id else None,
        )

        # 扣除余额
        balance_obj.balance -= amount
        balance_obj.total_consumed += amount
        balance_obj.save()

        serializer = PaymentSerializer(payment)
        return Response(serializer.data, status=201)

    @action(detail=False, methods=['post'])
    def refund(self, request):
        """
        余额支付退款补偿（幂等）

        POST /api/v1/payments/balance/refund/
        {
            "transaction_id": "PAY_xxx",
            "reason": "预约失败自动补偿"
        }
        """
        transaction_id = request.data.get('transaction_id')
        reason = str(request.data.get('reason') or '预约失败自动补偿').strip()

        if not transaction_id:
            return Response({'detail': 'transaction_id 不能为空'}, status=400)

        with transaction.atomic():
            payment = Payment.objects.select_for_update().filter(
                user=request.user,
                transaction_id=transaction_id,
                method=Payment.Method.BALANCE,
            ).first()

            if not payment:
                return Response({'detail': '未找到可退款的余额支付订单'}, status=404)

            if payment.status == Payment.Status.REFUNDED:
                balance_obj, _ = UserBalance.objects.get_or_create(user=request.user)
                return Response({
                    'detail': '订单已退款',
                    'status': payment.status,
                    'balance': f"{balance_obj.balance:.2f}",
                })

            if payment.status != Payment.Status.SUCCESS:
                return Response({'detail': '当前订单状态不允许退款'}, status=400)

            balance_obj, _ = UserBalance.objects.select_for_update().get_or_create(user=request.user)
            refund_amount = payment.amount
            balance_obj.balance += refund_amount
            balance_obj.total_consumed = max(Decimal('0.00'), balance_obj.total_consumed - refund_amount)
            balance_obj.save(update_fields=['balance', 'total_consumed', 'updated_at'])

            payment.status = Payment.Status.REFUNDED
            if reason:
                base_remark = payment.remark or ''
                append_part = f"退款:{reason}"
                payment.remark = (f"{base_remark} | {append_part}" if base_remark else append_part)[:200]
            payment.save(update_fields=['status', 'remark'])

        return Response({
            'detail': '退款成功',
            'status': payment.status,
            'transaction_id': payment.transaction_id,
            'refund_amount': f"{refund_amount:.2f}",
            'balance': f"{balance_obj.balance:.2f}",
        })


class TopUpRecordViewSet(viewsets.ModelViewSet):
    """
    充值记录 — 用户查看自己的充值历史
    """
    serializer_class = TopUpRecordSerializer
    filterset_fields = ['payment_method', 'status']
    ordering_fields = ['created_at', 'amount']
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TopUpRecord.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """创建充值记录时自动关联当前用户"""
        serializer.save(user=self.request.user)


class BankCardViewSet(viewsets.ModelViewSet):
    """银行卡管理 — 用户绑定/解绑银行卡。"""
    serializer_class = BankCardSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['is_active', 'is_default']

    def get_queryset(self):
        return BankCard.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
