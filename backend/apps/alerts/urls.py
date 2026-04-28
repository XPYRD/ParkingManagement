"""
alerts — URL 路由

路由表：
/api/v1/alerts/alerts/     → 系统预警 CRUD + 统计 + 解决
/api/v1/alerts/tickets/    → 用户工单 CRUD
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'alerts'

router = DefaultRouter()
router.register('alerts', views.AlertViewSet, basename='alert')
router.register('tickets', views.TicketViewSet, basename='ticket')

urlpatterns = [
    path('', include(router.urls)),
]
