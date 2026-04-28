from django.db import migrations


def migrate_is_reserved_to_reserved_plate(apps, schema_editor):
    ParkingSpace = apps.get_model('parking', 'ParkingSpace')
    for spot in ParkingSpace.objects.filter(is_reserved=True):
        current = (spot.reserved_plate or '').strip()
        if not current:
            spot.reserved_plate = 'RESERVED'
            spot.save(update_fields=['reserved_plate'])


class Migration(migrations.Migration):

    dependencies = [
        ('parking', '0014_reservation_payment_fields'),
    ]

    operations = [
        migrations.RunPython(migrate_is_reserved_to_reserved_plate, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='parkingspace',
            name='is_reserved',
        ),
    ]
