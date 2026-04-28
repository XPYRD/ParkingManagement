from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parking', '0015_remove_parkingspace_is_reserved'),
    ]

    operations = [
        migrations.AddField(
            model_name='parkingspace',
            name='is_navigation_start',
            field=models.BooleanField(
                default=False,
                help_text='用于反向寻车时选择“我现在在这里”',
                verbose_name='是否导航起点',
            ),
        ),
        migrations.AddField(
            model_name='parkingspace',
            name='navigation_start_name',
            field=models.CharField(
                blank=True,
                default='',
                help_text='例如：电梯A、南出口、服务台',
                max_length=50,
                verbose_name='导航起点名称',
            ),
        ),
    ]
