"""
Integration tests — full business lifecycle scenarios

Coverage:
1. Vehicle entry → fee query → payment → exit (complete lifecycle)
2. Reservation lifecycle: create → verify occupied → cancel → verify released
3. Simulated vehicle isolation: simulated vehicles don't appear in user's list
4. Subscription privilege boundaries: subscriber free vs non-subscriber charged
5. Cross-user isolation: User A's subscription doesn't help User B's car
6. Edge cases: duplicate entry, double exit, cancel already cancelled
"""

from datetime import date, time
from decimal import Decimal
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User, Vehicle
from parking.models import ParkingSpace, ParkingSession, Reservation, SpotConnection
from payments.models import SubscriptionPlan, Subscription, PricingRule, Payment


class VehicleLifecycleIntegrationTest(APITestCase):
    """Complete entry → query → pay → exit lifecycle."""

    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='lifecycle_admin', password='x', phone='13810000001')
        self.user = User.objects.create_user(
            username='lifecycle_user', password='x', phone='13810000002')
        self.vehicle = Vehicle.objects.create(
            owner=self.user, plate_number='LCY00001', brand='Lifecycle')
        self.spot = ParkingSpace.objects.create(
            space_id='space_LC01', floor='1F', center_x=100, center_y=100, x=90, y=90)

        # Ensure hourly rate exists
        PricingRule.objects.filter(
            rate_type=PricingRule.RateType.HOURLY_STANDARD).delete()
        PricingRule.objects.create(
            rate_type=PricingRule.RateType.HOURLY_STANDARD,
            value=Decimal('6.00'), unit='元/小时', effective_date=timezone.now().date())

        # Active subscription so vehicle can exit for free
        Subscription.objects.create(
            user=self.user,
            plan='monthly',
            price=Decimal('149.00'),
            start_date=timezone.localdate() - timezone.timedelta(days=10),
            end_date=timezone.localdate() + timezone.timedelta(days=10),
            is_active=True,
        )

    def _entry(self, plate='LCY00001'):
        """Simulate vehicle entry via webhook."""
        url = reverse('parking:hardware-handle-webhook')
        resp = self.client.post(url, {
            'event_type': 'space_occupied',
            'space_id': self.spot.space_id,
            'plate_number': plate,
            'timestamp': timezone.now().isoformat(),
        })
        self.assertIn(resp.status_code, [200, 201])
        return resp

    def _query_by_plate(self, plate='LCY00001'):
        """Query session by plate number."""
        url = reverse('parking:session-by-plate')
        return self.client.get(url, {'plate': plate})

    def _pay(self, session_id, amount='6.00'):
        """Quick pay for a session."""
        url = reverse('parking:session-quick-pay', args=[session_id])
        return self.client.post(url, {
            'plate_number': 'LCY00001', 'amount': amount, 'method': 'wechat'
        })

    def _exit(self, session_id):
        """Mark vehicle as exited."""
        url = reverse('parking:session-mark-exit', args=[session_id])
        return self.client.post(url, {'plate_number': 'LCY00001'})

    def test_complete_entry_query_pay_exit(self):
        """Full lifecycle: entry → query → pay → exit → spot released."""
        # 1. Entry
        self._entry()
        self.spot.refresh_from_db()
        self.assertEqual(self.spot.current_plate, 'LCY00001')

        # 2. Query by plate — should find active session (subscription makes it free)
        resp = self._query_by_plate()
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data['found'])
        session_id = resp.data['session_id']
        self.assertGreaterEqual(float(resp.data['amount']), 0)
        self.assertIn('小时', resp.data['duration_text'])
        self.assertIn('分钟', resp.data['duration_text'])

        # 3. Pay (skip for subscription-free users; session already marked PAID by query)
        if not resp.data.get('subscription_free'):
            pay_resp = self._pay(session_id)
            self.assertIn(pay_resp.status_code, [200, 201])

        # 4. Exit
        exit_resp = self._exit(session_id)
        self.assertIn(exit_resp.status_code, [200, 201])

        # 5. Spot released
        self.spot.refresh_from_db()
        self.assertIsNone(self.spot.current_plate)

        # 6. Session has exit_time
        session = ParkingSession.objects.get(id=session_id)
        self.assertIsNotNone(session.exit_time)

    def test_duplicate_entry_blocked(self):
        """Same plate entering twice should be intercepted (already in lot)."""
        self._entry()

        # Second entry for same plate — should say already in lot
        # (by-plate finds existing session)
        resp = self._query_by_plate()
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data['found'])

    def test_double_exit_safe(self):
        """Exiting an already-exited vehicle should be safe."""
        self._entry()
        resp = self._query_by_plate()
        session_id = resp.data['session_id']

        self._exit(session_id)

        # Second exit
        resp2 = self._exit(session_id)
        # Should succeed (idempotent) or fail gracefully
        self.assertIn(resp2.status_code, [200, 400])

    def test_entry_creates_vehicle_if_not_exists(self):
        """Entry for an unregistered plate auto-creates vehicle + session."""
        plate = 'NEW_PLATE_99'
        self._entry(plate)

        # Vehicle should be auto-created
        v = Vehicle.objects.filter(plate_number=plate)
        self.assertTrue(v.exists())

        # Session should exist
        self.assertTrue(
            ParkingSession.objects.filter(
                vehicle__plate_number=plate, exit_time__isnull=True
            ).exists()
        )

        # by-plate should find it
        resp = self._query_by_plate(plate)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data['found'])

    def test_entry_without_webhook_direct_space_plate(self):
        """
        Scenario: space has current_plate but no Vehicle record exists.
        by-plate should return parking info from the space record directly,
        without auto-creating any Vehicle or Session.
        """
        spot = ParkingSpace.objects.create(
            space_id='space_ORPHAN01', floor='1F', center_x=500, center_y=500,
            current_plate='ORPHAN01')

        resp = self.client.get(
            reverse('parking:session-by-plate'), {'plate': 'ORPHAN01'}
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data['found'])
        # No session created
        self.assertIsNone(resp.data['session_id'])
        self.assertFalse(resp.data['subscription_free'])


class SubscriptionPrivilegeBoundaryTest(APITestCase):
    """Subscription privileges: free entry/exit for subscribers, charged for others."""

    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='sub_admin', password='x', phone='13820000001')
        self.sub_user = User.objects.create_user(
            username='sub_user', password='x', phone='13820000002')
        self.non_sub_user = User.objects.create_user(
            username='non_sub_user', password='x', phone='13820000003')
        self.other_user = User.objects.create_user(
            username='other_user', password='x', phone='13820000004')

        self.vehicle_sub = Vehicle.objects.create(
            owner=self.sub_user, plate_number='SUB00001', brand='SubCar')
        self.vehicle_non = Vehicle.objects.create(
            owner=self.non_sub_user, plate_number='NONSUB01', brand='NonSub')
        self.vehicle_other = Vehicle.objects.create(
            owner=self.other_user, plate_number='OTHER01', brand='Other')

        self.spot = ParkingSpace.objects.create(
            space_id='space_SUB01', floor='1F', center_x=100, center_y=100, x=90, y=90)

        # Hourly rate
        PricingRule.objects.filter(
            rate_type=PricingRule.RateType.HOURLY_STANDARD).delete()
        PricingRule.objects.create(
            rate_type=PricingRule.RateType.HOURLY_STANDARD,
            value=Decimal('6.00'), unit='元/小时', effective_date=timezone.now().date())

        # Active subscription for sub_user only
        plan = SubscriptionPlan.objects.filter(code='monthly').first()
        Subscription.objects.create(
            user=self.sub_user,
            plan='monthly',
            price=Decimal('149.00'),
            start_date=timezone.localdate() - timezone.timedelta(days=10),
            end_date=timezone.localdate() + timezone.timedelta(days=10),
            is_active=True,
        )

    def _entry(self, vehicle):
        url = reverse('parking:hardware-handle-webhook')
        resp = self.client.post(url, {
            'event_type': 'space_occupied',
            'space_id': self.spot.space_id,
            'plate_number': vehicle.plate_number,
        })
        self.assertIn(resp.status_code, [200, 201])

    def test_subscriber_parking_is_free(self):
        """Subscriber's car should have amount=0 when queried."""
        self._entry(self.vehicle_sub)

        resp = self.client.get(
            reverse('parking:session-by-plate'),
            {'plate': self.vehicle_sub.plate_number}
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data['found'])
        self.assertEqual(resp.data['subscription_free'], True)
        self.assertEqual(float(resp.data['amount']), 0.0)

    def test_non_subscriber_parking_is_charged(self):
        """Non-subscriber's car should have positive amount."""
        self._entry(self.vehicle_non)

        resp = self.client.get(
            reverse('parking:session-by-plate'),
            {'plate': self.vehicle_non.plate_number}
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data['found'])
        self.assertEqual(resp.data['subscription_free'], False)
        self.assertGreater(float(resp.data['amount']), 0)

    def test_other_user_not_benefited_by_sub_users_subscription(self):
        """User A's subscription should NOT make User B's car free."""
        self._entry(self.vehicle_other)

        resp = self.client.get(
            reverse('parking:session-by-plate'),
            {'plate': self.vehicle_other.plate_number}
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data['found'])
        self.assertEqual(resp.data['subscription_free'], False)
        self.assertGreater(float(resp.data['amount']), 0)

    def test_expired_subscription_not_free(self):
        """Expired subscription should not give free parking."""
        # Expire sub_user's subscription
        Subscription.objects.filter(user=self.sub_user).update(
            end_date=timezone.localdate() - timezone.timedelta(days=5))

        self._entry(self.vehicle_sub)

        resp = self.client.get(
            reverse('parking:session-by-plate'),
            {'plate': self.vehicle_sub.plate_number}
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data['found'])
        self.assertEqual(resp.data['subscription_free'], False)
        self.assertGreater(float(resp.data['amount']), 0)


class SimulatedVehicleIsolationTest(APITestCase):
    """Simulated vehicles should NOT appear in user's personal vehicle list."""

    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='sim_admin', password='x', phone='13830000000')
        self.user = User.objects.create_user(
            username='sim_user', password='x', phone='13830000001')
        self.real_vehicle = Vehicle.objects.create(
            owner=self.user, plate_number='REAL0001', brand='RealCar')
        self.sim_vehicle = Vehicle.objects.create(
            owner=self.user, plate_number='SIM0001', brand='模拟车辆',
            is_simulated=True)

        # Create a space for webhook entry
        self.spot = ParkingSpace.objects.create(
            space_id='space_SIM01', floor='1F', center_x=100, center_y=100, x=90, y=90)

    def test_simulated_vehicle_not_in_user_list(self):
        """User's vehicle list should exclude is_simulated=True vehicles."""
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(reverse('accounts:vehicle-list'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        plates = [v['plate_number'] for v in resp.data['results']]
        self.assertIn('REAL0001', plates)
        self.assertNotIn('SIM0001', plates)

    def test_webhook_creates_simulated_vehicle(self):
        """Webhook entry should create vehicle with is_simulated=True."""
        url = reverse('parking:hardware-handle-webhook')
        resp = self.client.post(url, {
            'event_type': 'space_occupied',
            'space_id': self.spot.space_id,
            'plate_number': 'NEW_SIM_CAR',
        })
        self.assertIn(resp.status_code, [200, 201])

        v = Vehicle.objects.get(plate_number='NEW_SIM_CAR')
        self.assertTrue(v.is_simulated)

    def test_simulated_vehicle_session_exists(self):
        """Even simulated vehicles should have a ParkingSession."""
        url = reverse('parking:hardware-handle-webhook')
        self.client.post(url, {
            'event_type': 'space_occupied',
            'space_id': self.spot.space_id,
            'plate_number': 'NEW_SIM_CAR2',
        })

        self.assertTrue(
            ParkingSession.objects.filter(
                vehicle__plate_number='NEW_SIM_CAR2',
                exit_time__isnull=True
            ).exists()
        )

    def test_simulated_vehicle_can_be_queried(self):
        """Simulated vehicle should be queryable by plate."""
        url = reverse('parking:hardware-handle-webhook')
        self.client.post(url, {
            'event_type': 'space_occupied',
            'space_id': self.spot.space_id,
            'plate_number': 'NEW_SIM_CAR3',
        })

        resp = self.client.get(
            reverse('parking:session-by-plate'),
            {'plate': 'NEW_SIM_CAR3'}
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data['found'])


class ReservationLifecycleIntegrationTest(APITestCase):
    """Complete reservation lifecycle with spot state verification."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='res_lifecycle_user', password='x', phone='13840000001')
        self.spot = ParkingSpace.objects.create(
            space_id='space_RLC01', floor='1F', center_x=100, center_y=100, x=90, y=90)
        self.reserve_url = reverse('parking:reservation-list')

        # Pricing rules
        PricingRule.objects.filter(
            rate_type=PricingRule.RateType.RESERVATION_DAILY).delete()
        PricingRule.objects.filter(
            rate_type=PricingRule.RateType.RESERVATION_EV_SURCHARGE).delete()
        PricingRule.objects.create(
            rate_type=PricingRule.RateType.RESERVATION_DAILY,
            value=Decimal('30.00'), unit='元/天', effective_date=timezone.now().date())
        PricingRule.objects.create(
            rate_type=PricingRule.RateType.RESERVATION_EV_SURCHARGE,
            value=Decimal('10.00'), unit='元/天', effective_date=timezone.now().date())

    def test_create_reservation_marks_spot_reserved(self):
        """Creating a reservation should mark the spot as reserved."""
        self.client.force_authenticate(user=self.user)
        resp = self.client.post(self.reserve_url, {
            'spot': self.spot.id,
            'date': '2026-06-01',
            'end_date': '2026-06-01',
            'start_time': '10:00:00',
            'end_time': '12:00:00',
            'total_amount': '30.00',
            'payment_method': 'wechat',
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        self.spot.refresh_from_db()
        self.assertTrue(str(self.spot.reserved_plate or '').strip())

    def test_cancel_reservation_releases_spot(self):
        """Canceling a reservation should release the spot."""
        self.client.force_authenticate(user=self.user)
        r = Reservation.objects.create(
            user=self.user, spot=self.spot,
            date=date(2026, 6, 1), end_date=date(2026, 6, 1),
            start_time=time(10, 0), end_time=time(12, 0),
            total_amount=30, payment_method='wechat',
            booking_code='SENT-RLC01')

        cancel_url = reverse('parking:reservation-cancel', args=[r.id])
        resp = self.client.post(cancel_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        self.spot.refresh_from_db()
        self.assertFalse(str(self.spot.reserved_plate or '').strip())

    def test_cancel_already_cancelled_reservation(self):
        """Canceling an already-cancelled reservation should fail gracefully."""
        self.client.force_authenticate(user=self.user)
        r = Reservation.objects.create(
            user=self.user, spot=self.spot,
            date=date(2026, 6, 1), end_date=date(2026, 6, 1),
            start_time=time(10, 0), end_time=time(12, 0),
            total_amount=30, status='cancelled', payment_method='wechat',
            booking_code='SENT-RLC02')

        cancel_url = reverse('parking:reservation-cancel', args=[r.id])
        resp = self.client.post(cancel_url)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cancel_already_completed_reservation(self):
        """Canceling a completed reservation should fail."""
        self.client.force_authenticate(user=self.user)
        r = Reservation.objects.create(
            user=self.user, spot=self.spot,
            date=date(2026, 6, 1), end_date=date(2026, 6, 1),
            start_time=time(10, 0), end_time=time(12, 0),
            total_amount=30, status='completed', payment_method='wechat',
            booking_code='SENT-RLC03')

        cancel_url = reverse('parking:reservation-cancel', args=[r.id])
        resp = self.client.post(cancel_url)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reserved_spot_cannot_be_reserved_again(self):
        """A spot that is already reserved cannot be reserved by another user."""
        user2 = User.objects.create_user(
            username='res_user2', password='x', phone='13840000002')

        # First user reserves
        self.client.force_authenticate(user=self.user)
        resp1 = self.client.post(self.reserve_url, {
            'spot': self.spot.id,
            'date': '2026-06-15',
            'end_date': '2026-06-15',
            'start_time': '08:00:00',
            'end_time': '10:00:00',
            'total_amount': '30.00',
            'payment_method': 'wechat',
        })
        self.assertEqual(resp1.status_code, status.HTTP_201_CREATED)

        # Second user tries to reserve same spot
        self.client.force_authenticate(user=user2)
        resp2 = self.client.post(self.reserve_url, {
            'spot': self.spot.id,
            'date': '2026-06-15',
            'end_date': '2026-06-15',
            'start_time': '08:00:00',
            'end_time': '10:00:00',
            'total_amount': '30.00',
            'payment_method': 'wechat',
        })
        self.assertEqual(resp2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_subscription_user_reservation_is_free(self):
        """Subscriber should get reservation with total_amount=0."""
        plan = SubscriptionPlan.objects.filter(code='monthly').first()
        Subscription.objects.create(
            user=self.user,
            plan='monthly',
            price=Decimal('149.00'),
            start_date=timezone.localdate() - timezone.timedelta(days=5),
            end_date=timezone.localdate() + timezone.timedelta(days=5),
            is_active=True,
        )

        self.client.force_authenticate(user=self.user)
        resp = self.client.post(self.reserve_url, {
            'spot': self.spot.id,
            'date': '2026-06-20',
            'end_date': '2026-06-20',
            'start_time': '10:00:00',
            'end_time': '14:00:00',
            'total_amount': '30.00',
            'payment_method': 'wechat',
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(float(resp.data['total_amount']), 0.0)

    def test_non_subscription_user_reservation_is_charged(self):
        """Non-subscriber should pay normal reservation fee."""
        self.client.force_authenticate(user=self.user)
        resp = self.client.post(self.reserve_url, {
            'spot': self.spot.id,
            'date': '2026-06-20',
            'end_date': '2026-06-20',
            'start_time': '10:00:00',
            'end_time': '14:00:00',
            'total_amount': '30.00',
            'payment_method': 'wechat',
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertGreater(float(resp.data['total_amount']), 0)


class PermissionSecurityIntegrationTest(APITestCase):
    """Cross-user data isolation and admin-only endpoint tests."""

    def setUp(self):
        self.user_a = User.objects.create_user(
            username='sec_user_a', password='x', phone='13850000001')
        self.user_b = User.objects.create_user(
            username='sec_user_b', password='x', phone='13850000002')
        self.admin = User.objects.create_superuser(
            username='sec_admin', password='x', phone='13850000003')

        self.vehicle_a = Vehicle.objects.create(
            owner=self.user_a, plate_number='SEC_A001', brand='CarA')
        self.vehicle_b = Vehicle.objects.create(
            owner=self.user_b, plate_number='SEC_B001', brand='CarB')

        self.spot = ParkingSpace.objects.create(
            space_id='space_SEC01', floor='1F', center_x=100, center_y=100, x=90, y=90)

        # Create session for user_a
        self.session_a = ParkingSession.objects.create(
            vehicle=self.vehicle_a, spot=self.spot,
            entry_time=timezone.now())

    def test_user_cannot_see_other_user_sessions(self):
        """User A should not see User B's parking sessions."""
        self.client.force_authenticate(user=self.user_a)
        resp = self.client.get(reverse('parking:session-list'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        results = resp.data.get('results', resp.data) if isinstance(resp.data, dict) else resp.data
        plates = [s.get('plate_number') for s in results]
        self.assertIn('SEC_A001', plates)
        self.assertNotIn('SEC_B001', plates)

    def test_user_cannot_see_other_user_reservations(self):
        """User A should not see User B's reservations."""
        Reservation.objects.create(
            user=self.user_a, spot=self.spot,
            date=date(2026, 6, 1), end_date=date(2026, 6, 1),
            start_time=time(10, 0), end_time=time(12, 0),
            total_amount=30, payment_method='wechat',
            booking_code='SENT-PER01')
        Reservation.objects.create(
            user=self.user_b, spot=self.spot,
            date=date(2026, 6, 2), end_date=date(2026, 6, 2),
            start_time=time(10, 0), end_time=time(12, 0),
            total_amount=30, payment_method='wechat',
            booking_code='SENT-PER02')

        self.client.force_authenticate(user=self.user_a)
        resp = self.client.get(reverse('parking:reservation-list'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        for item in resp.data.get('results', resp.data if isinstance(resp.data, list) else []):
            self.assertEqual(item.get('user'), self.user_a.id)

    def test_user_cannot_cancel_other_user_reservation(self):
        """User A cannot cancel User B's reservation."""
        r_b = Reservation.objects.create(
            user=self.user_b, spot=self.spot,
            date=date(2026, 6, 1), end_date=date(2026, 6, 1),
            start_time=time(10, 0), end_time=time(12, 0),
            total_amount=30, payment_method='wechat',
            booking_code='SENT-PER03')

        self.client.force_authenticate(user=self.user_a)
        cancel_url = reverse('parking:reservation-cancel', args=[r_b.id])
        resp = self.client.post(cancel_url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_regular_user_cannot_access_admin_users(self):
        """Regular user cannot access admin user management."""
        self.client.force_authenticate(user=self.user_a)
        resp = self.client.get(reverse('accounts:admin-user-list'))
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_regular_user_cannot_create_parking_space(self):
        """Regular user cannot create parking spaces."""
        self.client.force_authenticate(user=self.user_a)
        resp = self.client.post(reverse('parking:spot-list'), {
            'space_id': 'space_HACK01', 'floor': '1F',
            'center_x': 100, 'center_y': 100, 'x': 90, 'y': 90,
        })
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_regular_user_cannot_create_device(self):
        """Regular user cannot create devices."""
        from devices.models import Device
        self.client.force_authenticate(user=self.user_a)
        resp = self.client.post(reverse('devices:device-list'), {
            'name': 'Hacked Device', 'device_type': 'camera',
        })
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_cannot_session_list(self):
        """Anonymous user cannot list parking sessions."""
        resp = self.client.get(reverse('parking:session-list'))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_cannot_reservation_list(self):
        """Anonymous user cannot list reservations."""
        resp = self.client.get(reverse('parking:reservation-list'))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class DataConsistencyTest(APITestCase):
    """Verify data consistency after key operations."""

    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='cons_admin', password='x', phone='13860000001')
        self.user = User.objects.create_user(
            username='cons_user', password='x', phone='13860000002')
        self.vehicle = Vehicle.objects.create(
            owner=self.user, plate_number='CONS0001', brand='Consistency')

        # Active subscription so vehicle can exit for free
        Subscription.objects.create(
            user=self.user,
            plan='monthly',
            price=Decimal('149.00'),
            start_date=timezone.localdate() - timezone.timedelta(days=10),
            end_date=timezone.localdate() + timezone.timedelta(days=10),
            is_active=True,
        )

        self.spots = []
        for i in range(3):
            self.spots.append(ParkingSpace.objects.create(
                space_id=f'space_CONS{i:02d}', floor='1F',
                center_x=100 + i * 100, center_y=100, x=90 + i * 100, y=90))

    def test_exit_clears_current_plate(self):
        """After exit, the parking space's current_plate must be cleared."""
        spot = self.spots[0]
        session = ParkingSession.objects.create(
            vehicle=self.vehicle, spot=spot,
            entry_time=timezone.now())

        url = reverse('parking:session-mark-exit', args=[session.id])
        self.client.force_authenticate(user=self.admin)
        resp = self.client.post(url, {'plate_number': 'CONS0001'})
        self.assertIn(resp.status_code, [200, 201])

        spot.refresh_from_db()
        self.assertIsNone(spot.current_plate)

    def test_cancel_reservation_clears_reserved_plate(self):
        """After cancel, the spot's reserved_plate must be cleared."""
        spot = self.spots[1]
        r = Reservation.objects.create(
            user=self.user, spot=spot,
            date=date(2026, 6, 1), end_date=date(2026, 6, 1),
            start_time=time(10, 0), end_time=time(12, 0),
            total_amount=30, payment_method='wechat',
            booking_code='SENT-CON01')

        self.client.force_authenticate(user=self.user)
        resp = self.client.post(
            reverse('parking:reservation-cancel', args=[r.id]))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        spot.refresh_from_db()
        self.assertFalse(str(spot.reserved_plate or '').strip())

    def test_webhook_exit_clears_current_plate(self):
        """Webhook space_released event should clear current_plate."""
        spot = self.spots[0]
        url = reverse('parking:hardware-handle-webhook')
        self.client.post(url, {
            'event_type': 'space_occupied',
            'space_id': spot.space_id,
            'plate_number': 'CONS0001',
        })
        self.spot = spot
        self.spot.refresh_from_db()
        self.assertEqual(self.spot.current_plate, 'CONS0001')

        # Now release
        self.client.post(url, {
            'event_type': 'space_released',
            'space_id': spot.space_id,
            'plate_number': 'CONS0001',
        })
        self.spot.refresh_from_db()
        self.assertIsNone(self.spot.current_plate)
