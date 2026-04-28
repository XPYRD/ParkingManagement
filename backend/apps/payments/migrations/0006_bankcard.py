from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0005_pricing_rule_reservation'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BankCard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bank_name', models.CharField(max_length=50, verbose_name='银行名称')),
                ('card_type', models.CharField(blank=True, default='', max_length=20, verbose_name='卡类型')),
                ('holder_name', models.CharField(max_length=50, verbose_name='持卡人姓名')),
                ('card_last4', models.CharField(max_length=4, verbose_name='卡号后4位')),
                ('bin_prefix', models.CharField(blank=True, default='', max_length=8, verbose_name='BIN前缀')),
                ('is_default', models.BooleanField(default=True, verbose_name='是否默认卡')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否有效')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('user', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='bank_cards', to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
            options={
                'verbose_name': '银行卡',
                'verbose_name_plural': '银行卡',
                'db_table': 'sentinel_bank_card',
                'ordering': ['-is_default', '-updated_at', '-id'],
            },
        ),
    ]
