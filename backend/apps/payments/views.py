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
from math import ceil
from datetime import timedelta
from decimal import Decimal, InvalidOperation
from urllib.parse import quote_plus
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.models import Vehicle
from parking.models import ParkingSession, ParkingSpace
from .models import Payment, Subscription, SubscriptionPlan, PricingRule, UserBalance, TopUpRecord
from .serializers import (
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

    def get_permissions(self):
        if self.action in ('quick_pay', 'quick_pay_quote', 'quick_pay_mark_exit'):
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(user=user)

    @staticmethod
    def _build_sandbox_qr(transaction_id, amount, method, biz_type='parking_pay'):
        payload = f"SANDBOX|{biz_type}|{transaction_id}|{amount}|{method}"
        return f"https://api.qrserver.com/v1/create-qr-code/?size=260x260&data={quote_plus(payload)}"

    @staticmethod
    def _get_or_create_guest_user():
        User = get_user_model()
        guest, created = User.objects.get_or_create(
            username='guest_quickpay',
            defaults={
                'email': 'guest_quickpay@sentinel.local',
                'is_active': True,
            },
        )
        if created:
            guest.set_unusable_password()
            guest.save(update_fields=['password'])
        return guest

    @staticmethod
    def _find_active_session(plate_number, session_id=None):
        """根据会话ID或车牌查询当前在场停车会话。"""
        qs = ParkingSession.objects.select_related('vehicle', 'vehicle__owner').filter(exit_time__isnull=True)
        if session_id:
            return qs.filter(id=session_id).first()
        if not plate_number:
            return None

        def normalize(value):
            return str(value or '').upper().replace('·', '').replace('.', '').replace(' ', '').strip()

        query_norm = normalize(plate_number)
        for session in qs.order_by('-entry_time').iterator():
            candidate = normalize(session.vehicle.plate_number)
            if candidate == query_norm or candidate.endswith(query_norm):
                return session
        return None

    @staticmethod
    def _normalize_plate(value):
        return str(value or '').upper().replace('·', '').replace('.', '').replace(' ', '').strip()

    @classmethod
    def _find_space_by_plate(cls, plate_number):
        query_norm = cls._normalize_plate(plate_number)
        spaces = ParkingSpace.objects.exclude(current_plate__isnull=True).exclude(current_plate='')
        for item in spaces.iterator():
            cand = cls._normalize_plate(item.current_plate)
            if cand == query_norm or cand.endswith(query_norm):
                return item
        return None

    @classmethod
    def _get_or_create_active_session(cls, plate_number):
        session = cls._find_active_session(plate_number)
        if session is not None:
            return session

        space = cls._find_space_by_plate(plate_number)
        if space is None:
            return None

        query_norm = cls._normalize_plate(plate_number)
        matched_vehicle = None
        for vehicle in Vehicle.objects.select_related('owner').all().iterator():
            cand = cls._normalize_plate(vehicle.plate_number)
            if cand == query_norm or cand.endswith(query_norm):
                matched_vehicle = vehicle
                break

        if matched_vehicle is None:
            guest = cls._get_or_create_guest_user()
            source_plate = str(space.current_plate or plate_number).upper().replace(' ', '').strip()
            if not source_plate:
                source_plate = cls._normalize_plate(plate_number)

            matched_vehicle = Vehicle.objects.create(
                owner=guest,
                plate_number=source_plate,
                brand='临时车辆',
                model='',
                color='',
                is_primary=False,
            )

        entry_time = space.bind_time or timezone.now()
        return ParkingSession.objects.create(
            vehicle=matched_vehicle,
            spot=space,
            entry_time=entry_time,
            amount=Decimal('0.00'),
            payment_status=ParkingSession.PaymentStatus.PENDING,
        )

    @staticmethod
    def _format_duration(total_minutes):
        hours = total_minutes // 60
        minutes = total_minutes % 60
        if hours and minutes:
            return f"{hours}小时{minutes}分钟"
        if hours:
            return f"{hours}小时"
        return f"{minutes}分钟"

    @classmethod
    def _compute_amount_from_start(cls, start_time):
        """从给定起算时间到当前时间计费：不足1小时按1小时。"""
        now = timezone.now()
        elapsed_seconds = max(0, (now - start_time).total_seconds())
        total_minutes = ceil(elapsed_seconds / 60)

        hourly_rate = PricingRule.get_active_value(
            PricingRule.RateType.HOURLY_STANDARD,
            Decimal('6.00'),
        ) or Decimal('6.00')

        chargeable_hours = max(1, ceil(elapsed_seconds / 3600))
        amount = (Decimal(chargeable_hours) * Decimal(hourly_rate)).quantize(Decimal('0.01'))

        return {
            'parked_minutes': total_minutes,
            'duration_text': cls._format_duration(total_minutes),
            'chargeable_minutes': total_minutes,
            'chargeable_hours': chargeable_hours,
            'hourly_rate': Decimal(hourly_rate).quantize(Decimal('0.01')),
            'grace_minutes': 0,
            'amount': amount,
        }

    @staticmethod
    def _has_active_subscription(user):
        """用户是否拥有当前有效订阅。"""
        if not user:
            return False
        today = timezone.localdate()
        return Subscription.objects.filter(
            user=user,
            is_active=True,
            start_date__lte=today,
            end_date__gte=today,
        ).exists()

    @classmethod
    def _build_quote_for_session(cls, session):
        """构建会话报价，并处理缴费后30分钟待出场逻辑。"""
        if session and cls._has_active_subscription(session.vehicle.owner):
            if session.amount != Decimal('0.00') or session.payment_status != ParkingSession.PaymentStatus.PAID:
                session.amount = Decimal('0.00')
                session.payment_status = ParkingSession.PaymentStatus.PAID
                session.save(update_fields=['amount', 'payment_status'])

            return {
                'entry_time': session.entry_time,
                'session_id': session.id,
                'parked_minutes': 0,
                'duration_text': '订阅有效期内，免费停车',
                'chargeable_minutes': 0,
                'chargeable_hours': 0,
                'grace_minutes': 0,
                'hourly_rate': '0.00',
                'amount': '0.00',
                'currency': 'CNY',
                'found': True,
                'payment_state': 'subscription_free',
                'leave_tip': '当前订阅有效，车辆进出场免费。',
            }

        now = timezone.now()
        latest_success_payment = Payment.objects.filter(
            session=session,
            status=Payment.Status.SUCCESS,
        ).order_by('-created_at').first()

        if latest_success_payment and session.payment_status == ParkingSession.PaymentStatus.PAID:
            leave_deadline = latest_success_payment.created_at + timedelta(minutes=30)
            if now <= leave_deadline:
                remain_minutes = ceil((leave_deadline - now).total_seconds() / 60)
                return {
                    'entry_time': session.entry_time,
                    'session_id': session.id,
                    'parked_minutes': 0,
                    'duration_text': '已缴费，待出场',
                    'chargeable_minutes': 0,
                    'chargeable_hours': 0,
                    'grace_minutes': max(0, remain_minutes),
                    'hourly_rate': '0.00',
                    'amount': '0.00',
                    'currency': 'CNY',
                    'found': True,
                    'payment_state': 'pending_exit',
                    'leave_deadline': leave_deadline.isoformat(),
                    'leave_tip': '请在半小时内离场，超时将重新开始计费。',
                }

            # 超过30分钟仍未出场：恢复计费
            session.payment_status = ParkingSession.PaymentStatus.OVERSTAY
            session.save(update_fields=['payment_status'])
            restarted = cls._compute_amount_from_start(leave_deadline)
            restarted.update({
                'entry_time': session.entry_time,
                'session_id': session.id,
                'currency': 'CNY',
                'found': True,
                'payment_state': 'restarted',
                'leave_deadline': leave_deadline.isoformat(),
                'leave_tip': '已超过离场宽限期，已重新开始计费。',
            })
            restarted['hourly_rate'] = f"{Decimal(restarted['hourly_rate']):.2f}"
            restarted['amount'] = f"{Decimal(restarted['amount']):.2f}"
            return restarted

        quote = cls._compute_amount_from_start(session.entry_time)
        session.amount = quote['amount']
        session.payment_status = ParkingSession.PaymentStatus.PENDING
        session.save(update_fields=['amount', 'payment_status'])
        quote.update({
            'entry_time': session.entry_time,
            'session_id': session.id,
            'currency': 'CNY',
            'found': True,
            'payment_state': 'charging',
            'leave_tip': '缴费后请在半小时内离场。',
        })
        quote['hourly_rate'] = f"{Decimal(quote['hourly_rate']):.2f}"
        quote['amount'] = f"{Decimal(quote['amount']):.2f}"
        return quote

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

        qs = Payment.objects.filter(status=Payment.Status.SUCCESS)
        stats = qs.aggregate(
            total_revenue=Sum('amount'),
            total_count=Count('id'),
            avg_amount=Avg('amount'),
        )
        # 按支付方式统计占比 — 对应 _9 "支付类型占比" 饼图
        method_breakdown = list(
            qs.values('method').annotate(
                count=Count('id'),
                total=Sum('amount'),
            ).order_by('-total')
        )
        stats['method_breakdown'] = method_breakdown
        return Response(stats)

    @action(detail=False, methods=['post'], url_path='sandbox-create')
    def sandbox_create(self, request):
        """创建沙箱停车支付订单，返回二维码和待支付状态。"""
        amount_raw = request.data.get('amount')
        method = request.data.get('method')
        session_id = request.data.get('session_id')
        remark = request.data.get('remark', '停车费支付')

        if session_id:
            session = ParkingSession.objects.select_related('vehicle', 'vehicle__owner').filter(id=session_id).first()
            if session and self._has_active_subscription(session.vehicle.owner):
                if session.amount != Decimal('0.00') or session.payment_status != ParkingSession.PaymentStatus.PAID:
                    session.amount = Decimal('0.00')
                    session.payment_status = ParkingSession.PaymentStatus.PAID
                    session.save(update_fields=['amount', 'payment_status'])
                return Response({
                    'detail': '当前订阅有效，车辆进出场免费，无需支付。',
                    'payment_state': 'subscription_free',
                    'session_id': session.id,
                    'amount': '0.00',
                })

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

    @action(detail=False, methods=['post'], url_path='quick-pay')
    def quick_pay(self, request):
        """匿名快速缴费：按车牌查询会话并创建订单，支持未登录访问。"""
        plate_number = str(request.data.get('plate_number') or '').strip().upper()
        amount_raw = request.data.get('amount')
        method = request.data.get('method', Payment.Method.WECHAT)
        session_id = request.data.get('session_id')

        if not plate_number:
            return Response({'detail': 'plate_number 不能为空'}, status=400)

        if method not in {Payment.Method.WECHAT, Payment.Method.ALIPAY, Payment.Method.CARD}:
            return Response({'detail': '该支付方式不支持快速缴费'}, status=400)

        active_session = self._find_active_session(plate_number, session_id=session_id)
        if active_session is None:
            active_session = self._get_or_create_active_session(plate_number)

        pricing = self._build_quote_for_session(active_session) if active_session else None

        if pricing and pricing.get('payment_state') == 'subscription_free':
            return Response({
                'mode': 'quick_pay',
                'plate_number': plate_number,
                'amount': '0.00',
                'status': 'success',
                'session_id': active_session.id if active_session else None,
                'parked_minutes': pricing.get('parked_minutes', 0),
                'duration_text': pricing.get('duration_text', ''),
                'payment_state': 'subscription_free',
                'leave_tip': '当前订阅有效，车辆进出场免费，无需支付。',
            })

        if amount_raw in (None, ''):
            if pricing is None:
                return Response({'detail': '未找到该车牌在场停车记录，请先查询费用后再支付'}, status=404)
            amount = Decimal(str(pricing['amount']))
        else:
            try:
                amount = Decimal(str(amount_raw))
            except (InvalidOperation, TypeError, ValueError):
                return Response({'detail': '支付金额格式错误'}, status=400)

        if amount <= 0:
            return Response({'detail': '支付金额必须大于0'}, status=400)

        if active_session is not None:
            payer = active_session.vehicle.owner
        else:
            matched_vehicle = Vehicle.objects.select_related('owner').filter(plate_number=plate_number).first()
            payer = matched_vehicle.owner if matched_vehicle else self._get_or_create_guest_user()

        transaction_id = f"QPAY_{int(time.time() * 1000)}"
        payment = Payment.objects.create(
            user=payer,
            session=active_session,
            transaction_id=transaction_id,
            amount=amount,
            method=method,
            status=Payment.Status.SUCCESS,
            remark=f"匿名快速缴费|车牌:{plate_number}",
        )
        qr_code_url = self._build_sandbox_qr(transaction_id, amount, method, biz_type='quick_pay')

        leave_deadline = None
        if active_session is not None:
            active_session.payment_status = ParkingSession.PaymentStatus.PAID
            active_session.amount = amount
            active_session.save(update_fields=['payment_status', 'amount'])
            leave_deadline = (payment.created_at + timedelta(minutes=30)).isoformat()

        return Response({
            'mode': 'quick_pay',
            'payment_id': payment.id,
            'transaction_id': transaction_id,
            'plate_number': plate_number,
            'amount': f"{amount:.2f}",
            'method': method,
            'status': payment.status,
            'expires_in_seconds': 300,
            'qr_code_url': qr_code_url,
            'display_payload': f"{transaction_id}|{plate_number}|¥{amount:.2f}|{method}",
            'session_id': active_session.id if active_session else None,
            'parked_minutes': pricing['parked_minutes'] if pricing else None,
            'duration_text': pricing['duration_text'] if pricing else '',
            'payment_state': 'pending_exit',
            'leave_deadline': leave_deadline,
            'leave_tip': '缴费成功，请在半小时内离场，超时将重新开始计费。',
        }, status=201)

    @action(detail=False, methods=['post'], url_path='quick-pay/quote')
    def quick_pay_quote(self, request):
        """按车牌查询当前停车时长，并计算应付金额。"""
        plate_number = str(request.data.get('plate_number') or '').strip().upper()
        if not plate_number:
            return Response({'detail': 'plate_number 不能为空'}, status=400)

        active_session = self._find_active_session(plate_number)
        if active_session is None:
            active_session = self._get_or_create_active_session(plate_number)

        if active_session is None:
            # 兼容提示：若车位表里能找到车牌，说明停车态数据存在但会话未同步
            query_norm = self._normalize_plate(plate_number)
            exists_in_spaces = False
            for item in ParkingSpace.objects.exclude(current_plate__isnull=True).exclude(current_plate='').iterator():
                cand = self._normalize_plate(item.current_plate)
                if cand == query_norm or cand.endswith(query_norm):
                    exists_in_spaces = True
                    break

            return Response({
                'found': False,
                'plate_number': plate_number,
                'detail': '未找到该车牌在场停车记录',
                'hint': '车位表存在该车牌，但未找到在场计费会话，请检查会话同步' if exists_in_spaces else '',
            })

        quote = self._build_quote_for_session(active_session)
        quote['plate_number'] = plate_number
        quote['entry_time'] = active_session.entry_time.isoformat()
        return Response(quote)

    @action(detail=False, methods=['post'], url_path='quick-pay/mark-exit')
    def quick_pay_mark_exit(self, request):
        """模拟车辆已出场：用于验证缴费后半小时内离场流程。"""
        plate_number = str(request.data.get('plate_number') or '').strip().upper()
        session_id = request.data.get('session_id')

        if not plate_number and not session_id:
            return Response({'detail': 'plate_number 或 session_id 至少提供一个'}, status=400)

        session = None
        if session_id:
            session = ParkingSession.objects.select_related('spot', 'vehicle').filter(
                id=session_id,
                exit_time__isnull=True,
            ).first()
        if session is None and plate_number:
            session = self._find_active_session(plate_number)

        if session is None:
            return Response({'detail': '未找到在场会话'}, status=404)

        now = timezone.now()
        session.exit_time = now
        session.payment_status = ParkingSession.PaymentStatus.PAID
        session.save(update_fields=['exit_time', 'payment_status'])

        if session.spot:
            session.spot.current_plate = None
            session.spot.bind_time = None
            session.spot.save(update_fields=['current_plate', 'bind_time', 'last_updated'])

        return Response({
            'detail': '已模拟车辆出场',
            'session_id': session.id,
            'plate_number': session.vehicle.plate_number,
            'exit_time': now.isoformat(),
        })


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
        """创建订阅时自动关联当前用户"""
        plan_ref_id = self.request.data.get('plan_ref_id')
        if plan_ref_id:
            plan_ref = SubscriptionPlan.objects.filter(id=plan_ref_id, is_active=True).first()
            if plan_ref:
                serializer.save(
                    user=self.request.user,
                    plan_ref=plan_ref,
                    plan=plan_ref.code,
                    price=plan_ref.price,
                )
                return

        plan_code = self.request.data.get('plan')
        plan_ref = SubscriptionPlan.objects.filter(code=plan_code, is_active=True).first()
        if plan_ref:
            serializer.save(
                user=self.request.user,
                plan_ref=plan_ref,
                plan=plan_ref.code,
                price=plan_ref.price,
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

    @staticmethod
    def _get_topup_discount_rate(amount: Decimal) -> Decimal:
        """充值优惠：1-100九折，100-500八折，500以上7.5折。"""
        if amount <= Decimal('100'):
            return Decimal('0.90')
        if amount <= Decimal('500'):
            return Decimal('0.80')
        return Decimal('0.75')

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

        discount_rate = self._get_topup_discount_rate(amount)
        payable_amount = (amount * discount_rate).quantize(Decimal('0.01'))

        # 创建充值记录（先置为待支付）
        topup_id = f"TOPUP_{request.user.id}_{int(time.time() * 1000)}"
        topup = TopUpRecord.objects.create(
            user=request.user,
            transaction_id=topup_id,
            amount=amount,
            payment_method=payment_method,
            status=TopUpRecord.Status.PENDING
        )
        qr_code_url = self._build_sandbox_qr(topup_id, payable_amount, payment_method)

        return Response({
            'mode': 'sandbox',
            'transaction_id': topup_id,
            'amount': f"{amount:.2f}",
            'recharge_amount': f"{amount:.2f}",
            'payable_amount': f"{payable_amount:.2f}",
            'discount_rate': f"{discount_rate:.2f}",
            'discount_percent': f"{(discount_rate * Decimal('100')).quantize(Decimal('0.1'))}%",
            'payment_method': payment_method,
            'status': TopUpRecord.Status.PENDING,
            'expires_in_seconds': 300,
            'qr_code_url': qr_code_url,
            'display_payload': f"{topup_id}|¥{payable_amount:.2f}|{payment_method}",
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
            discount_rate = self._get_topup_discount_rate(topup.amount)
            payable_amount = (topup.amount * discount_rate).quantize(Decimal('0.01'))
            return Response({
                'detail': '订单已入账',
                'status': topup.status,
                'balance': f"{balance_obj.balance:.2f}",
                'recharge_amount': f"{topup.amount:.2f}",
                'payable_amount': f"{payable_amount:.2f}",
            })

        topup.status = TopUpRecord.Status.SUCCESS if success else TopUpRecord.Status.FAILED
        topup.save(update_fields=['status'])

        if topup.status == TopUpRecord.Status.SUCCESS:
            balance_obj, _ = UserBalance.objects.get_or_create(user=request.user)
            balance_obj.balance += topup.amount
            balance_obj.total_recharged += topup.amount
            balance_obj.save(update_fields=['balance', 'total_recharged', 'updated_at'])
            discount_rate = self._get_topup_discount_rate(topup.amount)
            payable_amount = (topup.amount * discount_rate).quantize(Decimal('0.01'))
            return Response({
                'detail': '充值成功',
                'status': topup.status,
                'amount': f"{topup.amount:.2f}",
                'recharge_amount': f"{topup.amount:.2f}",
                'payable_amount': f"{payable_amount:.2f}",
                'discount_rate': f"{discount_rate:.2f}",
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

        if session_id:
            session = ParkingSession.objects.select_related('vehicle', 'vehicle__owner').filter(id=session_id).first()
            if session and PaymentViewSet._has_active_subscription(session.vehicle.owner):
                if session.amount != Decimal('0.00') or session.payment_status != ParkingSession.PaymentStatus.PAID:
                    session.amount = Decimal('0.00')
                    session.payment_status = ParkingSession.PaymentStatus.PAID
                    session.save(update_fields=['amount', 'payment_status'])
                return Response({'detail': '当前订阅有效，车辆进出场免费，无需支付。'}, status=400)

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
            remark=remark,
            session_id=session_id if session_id else None
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
