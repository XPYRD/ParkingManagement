"""
payments — URL 路由

路由表：
/api/v1/payments/records/        → 支付记录 + 营收汇总
/api/v1/payments/subscriptions/  → 订阅管理
/api/v1/payments/rules/          → 定价规则
/api/v1/payments/balance/        → 用户余额管理
/api/v1/payments/topups/         → 充值记录
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'payments'

router = DefaultRouter()
router.register('records', views.PaymentViewSet, basename='payment')
router.register('subscriptions', views.SubscriptionViewSet, basename='subscription')
router.register('subscription-plans', views.SubscriptionPlanViewSet, basename='subscription-plan')
router.register('rules', views.PricingRuleViewSet, basename='pricing-rule')
router.register('balance', views.UserBalanceViewSet, basename='balance')
router.register('topups', views.TopUpRecordViewSet, basename='topup')

urlpatterns = [
    path('', include(router.urls)),
]
