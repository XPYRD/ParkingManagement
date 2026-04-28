"""
devices — URL 路由

路由表：
/api/v1/devices/list/             → 设备 CRUD + 概览 + 报告故障
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'devices'

router = DefaultRouter()
router.register('list', views.DeviceViewSet, basename='device')

urlpatterns = [
    path('', include(router.urls)),
]
