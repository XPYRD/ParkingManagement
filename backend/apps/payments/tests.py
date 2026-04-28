from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import User, Vehicle
from parking.models import ParkingSpot, ParkingSession
from payments.models import Payment, PricingRule

class PaymentSummaryTestCase(APITestCase):
    def setUp(self):
        self.summary_url = reverse('payments:payment-summary')
        self.admin_user = User.objects.create_user(username='admin', password='a', is_staff=True)
        self.normal_user = User.objects.create_user(username='normal', password='b')
        
        vehicle = Vehicle.objects.create(owner=self.normal_user, plate_number='测A·12345')
        spot = ParkingSpot.objects.create(spot_id='P1')
        from django.utils import timezone
        now = timezone.now()
        session1 = ParkingSession.objects.create(vehicle=vehicle, spot=spot, entry_time=now)
        session2 = ParkingSession.objects.create(vehicle=vehicle, spot=spot, entry_time=now)
        
        # Create successful payments
        Payment.objects.create(
            user=self.normal_user, session=session1, amount=20.00, 
            method=Payment.Method.WECHAT, status=Payment.Status.SUCCESS, transaction_id='TX001'
        )
        Payment.objects.create(
            user=self.normal_user, session=session2, amount=30.00, 
            method=Payment.Method.ALIPAY, status=Payment.Status.SUCCESS, transaction_id='TX002'
        )
        # Create a failed payment
        Payment.objects.create(
            user=self.normal_user, session=session2, amount=50.00, 
            method=Payment.Method.CARD, status=Payment.Status.FAILED, transaction_id='TX003'
        )

    def test_summary_requires_admin(self):
        """测试只有管理员可以访问收益汇总"""
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.get(self.summary_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_summary_data(self):
        """测试收益汇总数据准确性"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.summary_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 仅统计 success 的，总共 20+30 = 50
        self.assertEqual(response.data['total_revenue'], 50.00)
        self.assertEqual(response.data['total_count'], 2)
        self.assertEqual(response.data['avg_amount'], 25.00)

class PricingRuleTestCase(APITestCase):
    def setUp(self):
        self.rule_url = reverse('payments:pricing-rule-list')
        self.admin_user = User.objects.create_user(username='admin_boss', password='1', is_staff=True)
        self.normal_user = User.objects.create_user(username='client', password='2')
        from django.utils import timezone
        self.rule = PricingRule.objects.create(
            rate_type=PricingRule.RateType.HOURLY_STANDARD, value=10.00, unit='元/小时', effective_date=timezone.now().date()
        )

    def test_list_rules_public(self):
        """测试任何人都可以获取计费规则列表"""
        response = self.client.get(self.rule_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rule_types = {item['rate_type'] for item in response.data['results']}
        self.assertIn(PricingRule.RateType.HOURLY_STANDARD, rule_types)
        self.assertIn(PricingRule.RateType.RESERVATION_DAILY, rule_types)

    def test_update_rule_forbidden(self):
        """测试普通用户无权更改计费规则"""
        self.client.force_authenticate(user=self.normal_user)
        url = reverse('payments:pricing-rule-detail', kwargs={'pk': self.rule.pk})
        response = self.client.patch(url, {'value': 15.00})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_rule_admin(self):
        """测试管理员可以更改计费规则"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('payments:pricing-rule-detail', kwargs={'pk': self.rule.pk})
        response = self.client.patch(url, {'value': 15.00})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.rule.refresh_from_db()
        self.assertEqual(self.rule.value, 15.00)
