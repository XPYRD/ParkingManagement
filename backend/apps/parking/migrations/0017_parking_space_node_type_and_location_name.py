from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parking', '0016_parkingspace_navigation_start_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='parkingspace',
            name='node_type',
            field=models.CharField(
                choices=[('parking', '车位'), ('location', '地点')],
                default='parking',
                help_text='parking=真实车位, location=导航地点节点',
                max_length=20,
                verbose_name='节点类型',
            ),
        ),
        migrations.AddField(
            model_name='parkingspace',
            name='location_name',
            field=models.CharField(
                blank=True,
                default='',
                help_text='地点节点名称，例如：电梯A、南出口、服务台',
                max_length=50,
                verbose_name='地点名称',
            ),
        ),
        migrations.AlterField(
            model_name='parkingspace',
            name='qr_code_token',
            field=models.CharField(
                blank=True,
                default='',
                help_text='二维码唯一识别码，用户扫描该二维码后绑定车牌',
                max_length=100,
                unique=True,
                verbose_name='二维码唯一识别码',
            ),
        ),
        migrations.RemoveField(
            model_name='parkingspace',
            name='is_navigation_start',
        ),
        migrations.RemoveField(
            model_name='parkingspace',
            name='navigation_start_name',
        ),
        migrations.AddIndex(
            model_name='parkingspace',
            index=models.Index(fields=['node_type', 'floor'], name='parking_spa_node_ty_8c3b67_idx'),
        ),
    ]