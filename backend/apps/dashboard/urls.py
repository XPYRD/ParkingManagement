"""
dashboard — URL 路由

/api/v1/dashboard/overview/  → 管理后台仪表盘聚合数据
"""

from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('overview/', views.DashboardOverviewView.as_view(), name='overview'),
]
