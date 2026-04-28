"""payments — Django Admin 注册"""

from django.contrib import admin
from .models import Payment, Subscription, SubscriptionPlan, PricingRule, UserBalance, TopUpRecord


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'price', 'duration_days', 'is_active', 'is_recommended', 'sort_order']
    list_filter = ['code', 'is_active', 'is_recommended']
    search_fields = ['name', 'code']
    list_editable = ['is_active', 'is_recommended', 'sort_order']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'user', 'amount', 'method', 'status', 'created_at']
    list_filter = ['method', 'status']
    search_fields = ['transaction_id', 'user__username']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'price', 'start_date', 'end_date', 'is_active']
    list_filter = ['plan', 'is_active']
    search_fields = ['user__username']


@admin.register(PricingRule)
class PricingRuleAdmin(admin.ModelAdmin):
    list_display = ['rate_type', 'value', 'unit', 'is_active', 'effective_date']
    list_filter = ['rate_type', 'is_active']


@admin.register(UserBalance)
class UserBalanceAdmin(admin.ModelAdmin):
    list_display = ['user', 'balance', 'total_recharged', 'total_consumed', 'updated_at']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TopUpRecord)
class TopUpRecordAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'user', 'amount', 'payment_method', 'status', 'created_at']
    list_filter = ['payment_method', 'status']
    search_fields = ['transaction_id', 'user__username']
    readonly_fields = ['transaction_id', 'created_at']
