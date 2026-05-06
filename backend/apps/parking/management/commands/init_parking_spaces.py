"""
Django management command to initialize ParkingSpace test data

Usage:
    python manage.py init_parking_spaces --rows 4 --cols 6
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from parking.models import ParkingSpace
import uuid


class Command(BaseCommand):
    help = 'Initialize ParkingSpace records for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--rows',
            type=int,
            default=4,
            help='Number of rows in parking grid (default: 4)'
        )
        parser.add_argument(
            '--cols',
            type=int,
            default=6,
            help='Number of columns in parking grid (default: 6)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing ParkingSpace records before creating new ones'
        )
        parser.add_argument(
            '--floor',
            type=str,
            default='B2',
            help='Floor identifier (default: B2)'
        )
        parser.add_argument(
            '--all-floors',
            action='store_true',
            help='Initialize all three floors (B1, B2, B3)'
        )

    def handle(self, *args, **options):
        rows = options['rows']
        cols = options['cols']
        clear = options['clear']
        all_floors = options['all_floors']
        
        floors = ['B2', 'B1', '1F'] if all_floors else [options['floor']]

        # Clear existing records if requested
        if clear:
            count = ParkingSpace.objects.count()
            ParkingSpace.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS(f'[OK] Cleared {count} existing ParkingSpace records')
            )

        total_created = 0
        total_updated = 0

        for floor in floors:
            self.stdout.write(self.style.WARNING(f'\n[LOC] 正在初始化 {floor} 楼层...'))
            created_count = 0
            updated_count = 0

            for row in range(rows):
                for col in range(cols):
                    # Generate space_id
                    space_num = row * cols + col + 1
                    space_id = f'space_{floor}{str(space_num).zfill(3)}'
                    
                    # Generate coordinates (SVG-based)
                    x = col * 180 + 100
                    y = row * 120 + 100
                    
                    # Generate QR code token
                    qr_token = f'QR_{floor}_{space_num}_{timezone.now().strftime("%Y%m%d%H%M")}'
                    
                    # Create or update ParkingSpace
                    obj, created = ParkingSpace.objects.get_or_create(
                        space_id=space_id,
                        defaults={
                            'floor': floor,
                            'qr_code_token': qr_token,
                            'status': False,
                            'x': x,
                            'y': y,
                            'center_x': x + 40,
                            'center_y': y + 30,
                            'current_plate': None,
                            'bind_time': None,
                        }
                    )
                    
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1

            total = rows * cols
            total_created += created_count
            total_updated += updated_count
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'   [OK] {floor} 楼层完成: 创建={created_count}, 更新={updated_count}, 总数={total}'
                )
            )

        # Final summary
        self.stdout.write(self.style.SUCCESS(
            f'\n[OK] 所有楼层初始化完成:\n'
            f'   创建总数: {total_created}\n'
            f'   更新总数: {total_updated}\n'
            f'   涵盖楼层: {", ".join(floors)}'
        ))

        # Display API endpoints
        self.stdout.write(self.style.WARNING('\n[API] 可用的 API 端点:'))
        self.stdout.write('  - GET  /api/v1/map/spaces/')
        self.stdout.write('  - POST /api/v1/hardware/webhook/')
        self.stdout.write('  - POST /api/v1/parking_spaces/bind/')
        self.stdout.write('  - GET  /api/v1/map/find_car/?plate_number=JingA88888')
