"""
Django 管理命令：初始化设备数据

使用方法：
    python manage.py init_devices

作用：清空现有设备数据，添加 6 条模拟设备数据
（三层停车场每层出/入口各一个摄像头）
"""

from django.core.management.base import BaseCommand
from devices.models import Device
from datetime import date


class Command(BaseCommand):
    help = '清空设备数据并初始化 6 条摄像头设备（三层停车场每层出/入口各一个）'

    def handle(self, *args, **options):
        # 清空现有设备
        Device.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('[OK] 已清空所有设备'))

        # 初始化 6 条设备数据
        devices_data = [
            {
                'name': '入口摄像头 1',
                'device_type': Device.DeviceType.CAMERA,
                'location': 'B2 层 - 入口',
                'serial_number': 'CAM-B2-IN-001',
                'status': Device.Status.ONLINE,
                'uptime': 99.85,
                'last_maintenance': date(2026, 4, 20),
                'fault_detail': '',
            },
            {
                'name': '出口摄像头 1',
                'device_type': Device.DeviceType.CAMERA,
                'location': 'B2 层 - 出口',
                'serial_number': 'CAM-B2-OUT-001',
                'status': Device.Status.ONLINE,
                'uptime': 99.92,
                'last_maintenance': date(2026, 4, 18),
                'fault_detail': '',
            },
            {
                'name': '入口摄像头 2',
                'device_type': Device.DeviceType.CAMERA,
                'location': 'B1 层 - 入口',
                'serial_number': 'CAM-B1-IN-002',
                'status': Device.Status.ONLINE,
                'uptime': 99.80,
                'last_maintenance': date(2026, 4, 19),
                'fault_detail': '',
            },
            {
                'name': '出口摄像头 2',
                'device_type': Device.DeviceType.CAMERA,
                'location': 'B1 层 - 出口',
                'serial_number': 'CAM-B1-OUT-002',
                'status': Device.Status.ONLINE,
                'uptime': 99.88,
                'last_maintenance': date(2026, 4, 21),
                'fault_detail': '',
            },
            {
                'name': '入口摄像头 3',
                'device_type': Device.DeviceType.CAMERA,
                'location': '1F 层 - 入口',
                'serial_number': 'CAM-1F-IN-003',
                'status': Device.Status.ONLINE,
                'uptime': 99.95,
                'last_maintenance': date(2026, 4, 17),
                'fault_detail': '',
            },
            {
                'name': '出口摄像头 3',
                'device_type': Device.DeviceType.CAMERA,
                'location': '1F 层 - 出口',
                'serial_number': 'CAM-1F-OUT-003',
                'status': Device.Status.ONLINE,
                'uptime': 99.78,
                'last_maintenance': date(2026, 4, 22),
                'fault_detail': '',
            },
        ]

        # 批量创建设备
        devices = [Device(**data) for data in devices_data]
        Device.objects.bulk_create(devices)

        self.stdout.write(self.style.SUCCESS('[OK] 已成功创建 6 条设备数据'))
        for device in devices:
            self.stdout.write(f'  - {device.name} ({device.serial_number})')
