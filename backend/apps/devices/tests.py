"""
devices — API tests
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import User
from devices.models import Device


class DeviceAPITestCase(APITestCase):
    def setUp(self):
        self.list_url = reverse('devices:device-list')
        self.admin = User.objects.create_superuser(username='admin', password='x', phone='13800000001')
        self.user = User.objects.create_user(username='user', password='y', phone='13800000002')

        self.device = Device.objects.create(
            name='Camera-Main', device_type='camera', status=Device.Status.ONLINE,
            serial_number='SN-CAM-001', location='Main Entrance')

        Device.objects.create(
            name='Sensor-B1', device_type='sensor', status=Device.Status.ERROR,
            serial_number='SN-SEN-002', location='B1 Floor')

    # ---- list ----

    def test_list_authenticated(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(resp.data['results']), 2)

    def test_list_anonymous_forbidden(self):
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    # ---- create ----

    def test_create_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {
            'name': 'New-Camera', 'device_type': 'camera',
            'serial_number': 'SN-NEW-003', 'location': 'B2 Exit',
        }
        resp = self.client.post(self.list_url, data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_create_regular_user_forbidden(self):
        self.client.force_authenticate(user=self.user)
        data = {'name': 'Bad-Device', 'device_type': 'camera'}
        resp = self.client.post(self.list_url, data)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    # ---- update ----

    def test_update_admin(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('devices:device-detail', args=[self.device.id])
        resp = self.client.patch(url, {'name': 'Camera-Updated'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.device.refresh_from_db()
        self.assertEqual(self.device.name, 'Camera-Updated')

    def test_update_regular_user_forbidden(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('devices:device-detail', args=[self.device.id])
        resp = self.client.patch(url, {'name': 'Hacked'})
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    # ---- delete ----

    def test_delete_admin(self):
        self.client.force_authenticate(user=self.admin)
        device_to_delete = Device.objects.create(
            name='Temp', device_type='camera', serial_number='SN-TEMP')
        url = reverse('devices:device-detail', args=[device_to_delete.id])
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    # ---- overview ----

    def test_overview(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('devices:device-overview')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('total', resp.data)
        self.assertIn('online', resp.data)
        self.assertIn('faults', resp.data)
        self.assertIn('maintenance', resp.data)

    # ---- report_fault ----

    def test_report_fault(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('devices:device-report-fault', args=[self.device.id])
        resp = self.client.post(url, {'fault_detail': '信号丢失'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.device.refresh_from_db()
        self.assertEqual(self.device.status, Device.Status.ERROR)

    def test_report_fault_missing_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('devices:device-report-fault', args=[self.device.id])
        resp = self.client.post(url, {})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    # ---- filter by type ----

    def test_filter_by_type(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(f"{self.list_url}?device_type=camera")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        for item in resp.data['results']:
            self.assertEqual(item['device_type'], 'camera')

    # ---- filter by status ----

    def test_filter_by_status(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(f"{self.list_url}?status=error")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        for item in resp.data['results']:
            self.assertEqual(item['status'], 'error')
