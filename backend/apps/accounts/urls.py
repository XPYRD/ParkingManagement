"""
accounts — URL 路由

路由表：
/api/v1/accounts/register/                  → 注册
/api/v1/accounts/profile/                   → 个人信息
/api/v1/accounts/vehicles/                  → 车辆 CRUD
/api/v1/accounts/admin/users/               → [管理端] 用户管理
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'accounts'

router = DefaultRouter()
router.register('vehicles', views.VehicleViewSet, basename='vehicle')
router.register('admin/users', views.UserAdminViewSet, basename='admin-user')

urlpatterns = [
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('change-username/', views.ChangeUsernameView.as_view(), name='change-username'),
    path('2fa/setup/', views.TwoFactorSetupView.as_view(), name='two-factor-setup'),
    path('2fa/activate/', views.TwoFactorActivateView.as_view(), name='two-factor-activate'),
    path('', include(router.urls)),
]
