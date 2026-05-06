"""
parking — comprehensive API tests
"""
from datetime import date, time
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import User, Vehicle
from parking.models import ParkingSpace, ParkingSession, Reservation, SpotConnection


class ParkingSpaceTestCase(APITestCase):
    def setUp(self):
        self.spot_list_url = reverse('parking:spot-list')
        self.user = User.objects.create_user(username='parker', password='a')
        self.admin = User.objects.create_superuser(username='admin1', password='x', phone='13800000001')
        # Create test spaces matching actual ParkingSpace model
        ParkingSpace.objects.create(
            space_id='space_A001', floor='1F', center_x=100, center_y=100, x=90, y=90,
            current_plate='SuA12345')
        ParkingSpace.objects.create(
            space_id='space_A002', floor='1F', center_x=200, center_y=100, x=190, y=90)
        ParkingSpace.objects.create(
            space_id='space_B1_001', floor='B1', center_x=300, center_y=100, x=290, y=90,
            status=True)  # maintenance

    def test_list_spaces_anonymous(self):
        resp = self.client.get(self.spot_list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(resp.data['results']), 3)

    def test_filter_by_floor(self):
        resp = self.client.get(f"{self.spot_list_url}?floor=1F")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        for item in resp.data['results']:
            self.assertEqual(item['floor'], '1F')

    def test_filter_free_status(self):
        """Filter by free status (no current_plate, not reserved, not maintenance)"""
        resp = self.client.get(f"{self.spot_list_url}?status=free")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        ids = [r['spot_id'] for r in resp.data['results']]
        self.assertIn('space_A002', ids)
        self.assertNotIn('space_A001', ids)

    def test_filter_occupied_status(self):
        resp = self.client.get(f"{self.spot_list_url}?status=occupied")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        ids = [r['spot_id'] for r in resp.data['results']]
        self.assertIn('space_A001', ids)

    def test_filter_maintenance_status(self):
        resp = self.client.get(f"{self.spot_list_url}?status=maintenance")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        ids = [r['spot_id'] for r in resp.data['results']]
        self.assertIn('space_B1_001', ids)

    def test_filter_by_type_ev(self):
        ParkingSpace.objects.filter(space_id='space_A002').update(type=True)
        resp = self.client.get(f"{self.spot_list_url}?type=ev")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        ids = [r['spot_id'] for r in resp.data['results']]
        self.assertIn('space_A002', ids)
        self.assertNotIn('space_A001', ids)

    def test_create_spot_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {'space_id': 'space_C001', 'floor': 'B2', 'center_x': 50, 'center_y': 50, 'x': 40, 'y': 40}
        resp = self.client.post(self.spot_list_url, data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_create_spot_regular_user_forbidden(self):
        self.client.force_authenticate(user=self.user)
        data = {'space_id': 'space_C002', 'floor': 'B2', 'center_x': 50, 'center_y': 50, 'x': 40, 'y': 40}
        resp = self.client.post(self.spot_list_url, data)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_toggle_maintenance_admin(self):
        self.client.force_authenticate(user=self.admin)
        spot = ParkingSpace.objects.get(space_id='space_A002')
        url = reverse('parking:spot-toggle-maintenance', args=[spot.id])
        resp = self.client.post(url, {'maintenance': True})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        spot.refresh_from_db()
        self.assertTrue(spot.status)

    def test_floor_summary(self):
        resp = self.client.get(reverse('parking:spot-floor-summary'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)


class ReservationTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='reserver', password='b', phone='13800000002')
        self.spot = ParkingSpace.objects.create(
            space_id='space_R01', floor='1F', center_x=100, center_y=100, x=90, y=90)
        self.reserve_url = reverse('parking:reservation-list')

    def test_create_reservation(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'spot': self.spot.id,
            'date': '2026-05-10',
            'end_date': '2026-05-10',
            'start_time': '10:00:00',
            'end_time': '12:00:00',
            'total_amount': '30.00',
            'payment_method': 'wechat',
        }
        resp = self.client.post(self.reserve_url, data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_cancel_reservation(self):
        self.client.force_authenticate(user=self.user)
        from parking.models import Reservation as Res
        r = Res.objects.create(
            user=self.user, spot=self.spot, date=date(2026, 5, 10),
            end_date=date(2026, 5, 10), start_time=time(10, 0), end_time=time(12, 0),
            total_amount=30, payment_method='wechat')
        cancel_url = reverse('parking:reservation-cancel', args=[r.id])
        resp = self.client.post(cancel_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        r.refresh_from_db()
        self.assertEqual(r.status, Res.Status.CANCELLED)


class SessionTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='driver', password='c', phone='13800000003')
        self.vehicle = Vehicle.objects.create(owner=self.user, plate_number='SuA00000', brand='Test')
        self.spot = ParkingSpace.objects.create(
            space_id='space_S01', floor='1F', center_x=100, center_y=100, x=90, y=90)
        self.session_url = reverse('parking:session-list')

    def test_create_session_admin(self):
        admin = User.objects.create_superuser(username='admin2', password='x', phone='13800000004')
        self.client.force_authenticate(user=admin)
        data = {
            'vehicle': self.vehicle.id,
            'spot': self.spot.id,
            'entry_time': timezone.now().isoformat(),
        }
        resp = self.client.post(self.session_url, data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_current_sessions(self):
        self.client.force_authenticate(user=self.user)
        session = ParkingSession.objects.create(
            vehicle=self.vehicle, spot=self.spot,
            entry_time=timezone.now() - timezone.timedelta(hours=2))
        current_url = reverse('parking:session-current')
        resp = self.client.get(current_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(resp.data), 1)

    def test_by_plate_not_found(self):
        """by-plate returns 404 when vehicle not found"""
        url = reverse('parking:session-by-plate')
        resp = self.client.get(f"{url}?plate=NOTEXIST")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_by_plate_found(self):
        """by-plate returns session info when vehicle exists"""
        session = ParkingSession.objects.create(
            vehicle=self.vehicle, spot=self.spot,
            entry_time=timezone.now() - timezone.timedelta(hours=1))
        url = reverse('parking:session-by-plate')
        resp = self.client.get(f"{url}?plate=SuA00000")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['plate_number'], 'SuA00000')

    def test_quick_pay(self):
        admin = User.objects.create_superuser(username='admin3', password='x', phone='13800000005')
        self.client.force_authenticate(user=admin)
        session = ParkingSession.objects.create(
            vehicle=self.vehicle, spot=self.spot,
            entry_time=timezone.now() - timezone.timedelta(hours=1))
        url = reverse('parking:session-quick-pay', args=[session.id])
        resp = self.client.post(url, {
            'plate_number': 'SuA00000', 'amount': 15.00, 'method': 'wechat'
        })
        self.assertIn(resp.status_code, [200, 201])

    def test_mark_exit(self):
        admin = User.objects.create_superuser(username='admin4', password='x', phone='13800000006')
        session = ParkingSession.objects.create(
            vehicle=self.vehicle, spot=self.spot,
            entry_time=timezone.now() - timezone.timedelta(hours=1))
        url = reverse('parking:session-mark-exit', args=[session.id])
        resp = self.client.post(url, {'plate_number': 'SuA00000'})
        self.assertIn(resp.status_code, [200, 201])
        session.refresh_from_db()
        self.assertIsNotNone(session.exit_time)


class NavigationTestCase(APITestCase):
    def setUp(self):
        self.a1 = ParkingSpace.objects.create(
            space_id='space_nav_A1', floor='1F', center_x=10, center_y=10, x=5, y=5)
        self.a2 = ParkingSpace.objects.create(
            space_id='space_nav_A2', floor='1F', center_x=20, center_y=10, x=15, y=5)
        SpotConnection.objects.create(from_spot=self.a1, to_spot=self.a2, distance=10)

    def test_find_path(self):
        url = reverse('parking:navigation-find-path')
        resp = self.client.post(url, {'from': self.a1.space_id, 'to': self.a2.space_id})
        self.assertIn(resp.status_code, [200, 400])


class AIRecognizeTestCase(APITestCase):
    """Test the AI plate recognition endpoint"""

    def test_recognize_missing_image(self):
        url = reverse('parking:ai_recognize_plate')
        resp = self.client.post(url, {})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', resp.data)

    def test_recognize_with_image(self):
        import io
        from PIL import Image
        url = reverse('parking:ai_recognize_plate')
        img = Image.new('RGB', (100, 100), color='white')
        buf = io.BytesIO()
        img.save(buf, 'PNG')
        buf.seek(0)
        buf.name = 'test_plate_SuA12345.png'
        resp = self.client.post(url, {'image': buf}, format='multipart')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # Should extract plate from filename
        if resp.data.get('success'):
            self.assertIn('plate_number', resp.data)
            self.assertIn('energy_type', resp.data)
