from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_remove_user_user_permissions'),
    ]

    operations = [
        migrations.RunSQL(
            sql='DROP TABLE IF EXISTS sentinel_ticket;',
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            sql='DROP TABLE IF EXISTS sentinel_alert;',
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
