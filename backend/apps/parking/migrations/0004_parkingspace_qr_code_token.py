# Generated migration for adding qr_code_token to ParkingSpace

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parking', '0003_parkingspace'),
    ]

    operations = [
        migrations.AddField(
            model_name='parkingspace',
            name='qr_code_token',
            field=models.CharField(
                help_text='二维码唯一识别码，用户扫描该二维码后绑定车牌',
                max_length=100,
                unique=True,
                default='',
                verbose_name='二维码唯一识别码'
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='parkingspace',
            name='bind_time',
            field=models.DateTimeField(
                blank=True,
                help_text='用户绑定车牌的时间',
                null=True,
                verbose_name='绑定时间'
            ),
        ),
        migrations.AddField(
            model_name='parkingspace',
            name='x',
            field=models.FloatField(
                blank=True,
                help_text='SVG相对坐标X，用于路径规划',
                null=True,
                verbose_name='SVG相对坐标X'
            ),
        ),
        migrations.AddField(
            model_name='parkingspace',
            name='y',
            field=models.FloatField(
                blank=True,
                help_text='SVG相对坐标Y，用于路径规划',
                null=True,
                verbose_name='SVG相对坐标Y'
            ),
        ),
    ]
