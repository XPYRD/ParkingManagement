"""
Sentinel Parking — 根路由配置

所有业务 API 统一挂载在 /api/v1/ 前缀下。
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from accounts.views import CustomTokenObtainPairView, TwoFactorVerifyView
from parking.views import (
    ai_recognize_plate, 
    MapViewSet, 
    HardwareWebhookViewSet, 
    get_map_svg,
    NavigationViewSet
)


urlpatterns = [
    # Django Admin 后台
    path('admin/', admin.site.urls),

    # JWT 认证端点（增加 2FA 拦截支持）
    path('api/v1/auth/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/auth/token/verify-2fa/', TwoFactorVerifyView.as_view(), name='two_factor_verify'),
    path('api/v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # 业务模块 API
    path('api/v1/accounts/', include('accounts.urls')),
    path('api/v1/parking/', include('parking.urls')),
    path('api/v1/payments/', include('payments.urls')),
    path('api/v1/devices/', include('devices.urls')),
    path('api/v1/alerts/', include('alerts.urls')),
    path('api/v1/dashboard/', include('dashboard.urls')),
    path('api/v1/ai/recognize/', ai_recognize_plate, name='ai_recognize_compat'),
    # 地图与硬件 webhook 兼容路由（与 /api/v1/parking/* 并存）
    path('api/v1/map/spaces/', MapViewSet.as_view({'get': 'get_spaces'}), name='map_spaces_compat'),
    path('api/v1/map/find_car/', MapViewSet.as_view({'get': 'find_car'}), name='map_find_car_compat'),
    path('api/v1/map/start-points/', MapViewSet.as_view({'get': 'get_start_points'}), name='map_start_points_compat'),
    path('api/v1/map/svg/', get_map_svg, name='map_svg_compat'),
    path('api/v1/hardware/webhook/', HardwareWebhookViewSet.as_view({'post': 'handle_webhook'}), name='hardware_webhook_compat'),

    # DRF Browsable API 登录（仅开发环境使用）
    path('api-auth/', include('rest_framework.urls')),
]

# 在开发环境下支持媒体文件访问 🚀
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
