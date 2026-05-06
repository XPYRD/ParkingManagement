"""
dashboard — API tests
"""
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import User, Vehicle
from parking.models import ParkingSpace, ParkingSession
from payments.models import Payment
from devices.models import Device


class DashboardOverviewTestCase(APITestCase):
    def setUp(self):
        self.url = reverse('dashboard:overview')
        self.admin = User.objects.create_superuser(username='admin', password='x', phone='13800000001')
        self.user = User.objects.create_user(username='user', password='y', phone='13800000002')

        # Create parking space
        self.spot = ParkingSpace.objects.create(
            space_id='space_D01', floor='1F', center_x=100, center_y=100, x=90, y=90)
        # Create occupied space
        ParkingSpace.objects.create(
            space_id='space_D02', floor='1F', center_x=200, center_y=100, x=190, y=90,
            current_plate='SuA00001')
        # Create maintenance space
        ParkingSpace.objects.create(
            space_id='space_D03', floor='B1', center_x=300, center_y=100, x=290, y=90,
            status=True)

        # Create vehicle and session
        self.vehicle = Vehicle.objects.create(owner=self.user, plate_number='SuA00001', brand='Test')
        self.session = ParkingSession.objects.create(
            vehicle=self.vehicle, spot=self.spot,
            entry_time=timezone.now() - timezone.timedelta(hours=2))

        # Create payment
        Payment.objects.create(
            user=self.user, session=self.session, amount=25.00,
            method=Payment.Method.WECHAT, status=Payment.Status.SUCCESS,
            transaction_id='TX_DASH_001')

        # Create device
        Device.objects.create(
            name='Camera-01', device_type='camera', status=Device.Status.ONLINE,
            serial_number='SN001', location='Entry Gate')

    # ---- auth ----

    def test_anonymous_forbidden(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_forbidden(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    # ---- admin access ----

    def test_admin_access_ok(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_daily_revenue(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.get(self.url)
        self.assertIn('daily_revenue', resp.data)

    def test_revenue_trend(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.get(self.url)
        self.assertIn('revenue_trend', resp.data)
        self.assertEqual(len(resp.data['revenue_trend']), 7)

    def test_occupancy_stats(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.get(self.url)
        occ = resp.data['occupancy']
        self.assertIn('total', occ)
        self.assertIn('occupied', occ)
        self.assertIn('free', occ)
        self.assertIn('maintenance', occ)
        self.assertIn('occupancy_rate', occ)
        self.assertGreater(occ['total'], 0)

    def test_floor_occupancy(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.get(self.url)
        self.assertIn('floor_occupancy', resp.data)

    def test_system_health(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.get(self.url)
        sh = resp.data['system_health']
        self.assertIn('total', sh)
        self.assertIn('online', sh)
        self.assertIn('server_load', sh)
        self.assertIn('network_latency', sh)
        self.assertIn('storage_usage', sh)

    def test_today_traffic(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.get(self.url)
        self.assertIn('today_traffic', resp.data)

    def test_hourly_traffic(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.get(self.url)
        self.assertIn('hourly_traffic', resp.data)
        self.assertEqual(len(resp.data['hourly_traffic']), 24)

    def test_recent_payments(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.get(self.url)
        self.assertIn('recent_payments', resp.data)

    def test_response_structure(self):
        """Verify all expected top-level keys are present."""
        self.client.force_authenticate(user=self.admin)
        resp = self.client.get(self.url)
        expected_keys = [
            'daily_revenue', 'revenue_trend', 'occupancy',
            'floor_occupancy', 'system_health', 'alerts',
            'today_traffic', 'hourly_traffic', 'recent_payments',
        ]
        for key in expected_keys:
            self.assertIn(key, resp.data, f'Missing key: {key}')
