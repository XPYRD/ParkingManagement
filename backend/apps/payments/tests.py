from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import User, Vehicle
from parking.models import ParkingSpace, ParkingSession
from payments.models import Payment, PricingRule, SubscriptionPlan, Subscription, BankCard


class PaymentSummaryTestCase(APITestCase):
    def setUp(self):
        self.summary_url = reverse('payments:payment-summary')
        self.admin_user = User.objects.create_user(username='admin', password='a', is_staff=True)
        self.normal_user = User.objects.create_user(username='normal', password='b')

        vehicle = Vehicle.objects.create(owner=self.normal_user, plate_number='测A·12345')
        spot = ParkingSpace.objects.create(space_id='P1')
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
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.get(self.summary_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_summary_data(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.summary_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_revenue'], 50.00)
        self.assertEqual(response.data['total_count'], 2)
        self.assertEqual(response.data['avg_amount'], 25.00)


class PaymentRecordsTestCase(APITestCase):
    def setUp(self):
        self.records_url = reverse('payments:payment-list')
        self.admin = User.objects.create_superuser(username='admin_pay', password='x', phone='13800000011')
        self.user = User.objects.create_user(username='payer', password='y', phone='13800000012')

        self.vehicle = Vehicle.objects.create(owner=self.user, plate_number='SuB00001', brand='Test')
        self.spot = ParkingSpace.objects.create(space_id='P2')
        from django.utils import timezone
        self.session = ParkingSession.objects.create(
            vehicle=self.vehicle, spot=self.spot, entry_time=timezone.now())

        self.payment = Payment.objects.create(
            user=self.user, session=self.session, amount=15.00,
            method=Payment.Method.WECHAT, status=Payment.Status.SUCCESS,
            transaction_id='TX_RECORD_001')

    def test_user_sees_own_payments(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(self.records_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(resp.data['results']), 1)

    def test_admin_sees_all_payments(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.get(self.records_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_sandbox_create_payment(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('payments:payment-sandbox-create')
        resp = self.client.post(url, {
            'amount': '20.00', 'method': 'wechat',
            'remark': '停车费支付',
        })
        self.assertIn(resp.status_code, [200, 201])


class SubscriptionPlanTestCase(APITestCase):
    def setUp(self):
        self.plans_url = reverse('payments:subscription-plan-list')
        self.admin = User.objects.create_superuser(username='admin_sub', password='x', phone='13800000013')
        self.user = User.objects.create_user(username='sub_user', password='y', phone='13800000014')

    def test_list_plans_authenticated(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(self.plans_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_update_plan_admin(self):
        self.client.force_authenticate(user=self.admin)
        plan = SubscriptionPlan.objects.filter(code='monthly').first()
        url = reverse('payments:subscription-plan-detail', args=[plan.id])
        resp = self.client.patch(url, {'price': '199.00'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_update_plan_user_forbidden(self):
        self.client.force_authenticate(user=self.user)
        plan = SubscriptionPlan.objects.filter(code='monthly').first()
        url = reverse('payments:subscription-plan-detail', args=[plan.id])
        resp = self.client.patch(url, {'price': '99.00'})
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


class BankCardTestCase(APITestCase):
    def setUp(self):
        self.cards_url = reverse('payments:bankcard-list')
        self.user = User.objects.create_user(username='cardholder', password='x', phone='13800000015')
        self.card = BankCard.objects.create(
            user=self.user, bank_name='工商银行', holder_name='张三',
            card_last4='5678', is_default=True)

    def test_list_own_cards(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(self.cards_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_add_card(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.post(self.cards_url, {
            'bank_name': '建设银行', 'holder_name': '张三',
            'card_last4': '1234', 'is_default': False,
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)


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
        response = self.client.get(self.rule_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rule_types = {item['rate_type'] for item in response.data['results']}
        self.assertIn(PricingRule.RateType.HOURLY_STANDARD, rule_types)
        self.assertIn(PricingRule.RateType.RESERVATION_DAILY, rule_types)

    def test_update_rule_forbidden(self):
        self.client.force_authenticate(user=self.normal_user)
        url = reverse('payments:pricing-rule-detail', kwargs={'pk': self.rule.pk})
        response = self.client.patch(url, {'value': 15.00})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_rule_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('payments:pricing-rule-detail', kwargs={'pk': self.rule.pk})
        response = self.client.patch(url, {'value': 15.00})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.rule.refresh_from_db()
        self.assertEqual(self.rule.value, 15.00)
