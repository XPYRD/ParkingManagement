"""
parking — URL 路由

路由表：
/api/v1/parking/spots/                      → 车位 CRUD + 楼层统计
/api/v1/parking/sessions/                   → 停车会话 + 当前活跃
/api/v1/parking/reservations/               → 预约 CRUD + 取消
/api/v1/parking/connections/                → 停车位连接（路径规划配置）
/api/v1/parking/navigation/find-path/       → 路径规划（Dijkstra）

新增（室内地图与反向寻车模块）：
/api/v1/map/spaces/                         → 全量车位状态
/api/v1/map/find_car/                       → 根据车牌号寻车
/api/v1/hardware/webhook/                   → 硬件推送的车位变化事件
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'parking'

router = DefaultRouter()
router.register('spots', views.ParkingSpotViewSet, basename='spot')
router.register('sessions', views.ParkingSessionViewSet, basename='session')
router.register('reservations', views.ReservationViewSet, basename='reservation')
router.register('connections', views.SpotConnectionViewSet, basename='connection')
router.register('navigation', views.NavigationViewSet, basename='navigation')

# 新增室内地图路由
router.register('map', views.MapViewSet, basename='map')
router.register('hardware', views.HardwareWebhookViewSet, basename='hardware')

urlpatterns = [
    path('map/svg/', views.get_map_svg, name='map_svg'),
    path('ai/recognize/', views.ai_recognize_plate, name='ai_recognize_plate'),
    path('', include(router.urls)),
]
