from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_user_totp_secret_user_two_factor_enabled'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='user_permissions',
        ),
    ]
