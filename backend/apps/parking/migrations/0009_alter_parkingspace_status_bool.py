from django.db import migrations, models


def convert_status_to_bool(apps, schema_editor):
    ParkingSpace = apps.get_model('parking', 'ParkingSpace')
    for row in ParkingSpace.objects.all().only('id', 'status'):
        raw = row.status
        raw_text = '' if raw is None else str(raw).strip().lower()
        # 兼容历史值：仅维护/损坏类状态映射为 True，其余视为正常(False)
        is_damaged = raw_text in {'maintenance', 'damaged', '1', 'true', 't', 'yes', 'y'}
        # 先写入字符 0/1，避免 MySQL 严格模式下从字符串到布尔转换报错
        ParkingSpace.objects.filter(id=row.id).update(status='1' if is_damaged else '0')


class Migration(migrations.Migration):

    dependencies = [
        ('parking', '0008_parkingspace_type'),
    ]

    operations = [
        migrations.RunPython(convert_status_to_bool, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='parkingspace',
            name='status',
            field=models.BooleanField(default=False, help_text='true=损坏, false=正常', verbose_name='是否损坏'),
        ),
    ]
