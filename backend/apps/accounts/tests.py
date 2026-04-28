from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import User, Vehicle

class AccountAPITestCase(APITestCase):
    def setUp(self):
        self.register_url = reverse('accounts:register')
        self.profile_url = reverse('accounts:profile')
        self.user = User.objects.create_user(
            username='testuser', 
            password='Password123!', 
            phone='13800000000',
            email='test@example.com'
        )

    def test_user_registration(self):
        """测试用户注册流程"""
        data = {
            'phone': '13912345678',
            'password': 'Password123!',
            'password_confirm': 'Password123!'
        }
        response = self.client.post(self.register_url, data)
        if response.status_code != 201:
            print("Register error:", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)

    def test_registration_duplicate_phone(self):
        """测试重复手机号拦截"""
        data = {
            'phone': '13800000000', # 同已存在用户
            'password': 'Password123!',
            'password_confirm': 'Password123!'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_profile(self):
        """测试获取个人资料"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['phone'], '13800000000')

    def test_update_profile(self):
        """测试更新资料属性"""
        self.client.force_authenticate(user=self.user)
        update_data = {
            'phone': '14000000000',
            'email': 'updated@example.com'
        }
        response = self.client.put(self.profile_url, update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.phone, '14000000000')
        self.assertEqual(self.user.email, 'updated@example.com')


class VehicleAPITestCase(APITestCase):
    def setUp(self):
        self.vehicle_list_url = reverse('accounts:vehicle-list')
        self.user = User.objects.create_user(username='carowner', password='Password123!')
        self.vehicle1 = Vehicle.objects.create(
            owner=self.user,
            plate_number='京A·88888',
            brand='特斯拉',
            model='Model 3',
            is_primary=True
        )

    def test_list_vehicles(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.vehicle_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['plate_number'], '京A·88888')

    def test_add_vehicle(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'plate_number': '沪B·99999',
            'brand': '宝马',
            'model': '5系',
            'color': 'white'
        }
        response = self.client.post(self.vehicle_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Vehicle.objects.filter(owner=self.user).count(), 2)
        
    def test_set_primary_vehicle(self):
        """测试设为默认车辆时，其它车辆应当自动取消默认"""
        self.client.force_authenticate(user=self.user)
        vehicle2 = Vehicle.objects.create(
            owner=self.user,
            plate_number='粤C·12345',
            brand='奥迪',
            is_primary=False
        )
        url = reverse('accounts:vehicle-set-primary', kwargs={'pk': vehicle2.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.vehicle1.refresh_from_db()
        vehicle2.refresh_from_db()
        
        self.assertFalse(self.vehicle1.is_primary)
        self.assertTrue(vehicle2.is_primary)
