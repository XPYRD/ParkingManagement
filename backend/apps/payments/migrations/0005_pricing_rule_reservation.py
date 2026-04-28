from decimal import Decimal

from django.db import migrations, models
from django.utils import timezone


def seed_reservation_pricing_rules(apps, schema_editor):
    PricingRule = apps.get_model('payments', 'PricingRule')
    today = timezone.now().date()

    defaults = [
        {
            'rate_type': 'reservation_daily',
            'value': Decimal('30.00'),
            'unit': '元/天',
            'description': '预约基础费，按天计费，不足一天按一天算',
            'is_active': True,
            'effective_date': today,
        },
        {
            'rate_type': 'reservation_ev_surcharge',
            'value': Decimal('10.00'),
            'unit': '元/单',
            'description': '预约充电桩附加费',
            'is_active': True,
            'effective_date': today,
        },
    ]

    for item in defaults:
        PricingRule.objects.update_or_create(
            rate_type=item['rate_type'],
            defaults={
                'value': item['value'],
                'unit': item['unit'],
                'description': item['description'],
                'is_active': item['is_active'],
                'effective_date': item['effective_date'],
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0004_subscription_plan_recommended'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pricingrule',
            name='rate_type',
            field=models.CharField(choices=[('hourly_standard', '标准时段（元/小时）'), ('hourly_peak', '高峰时段（元/小时）'), ('reservation_daily', '预约基础费（元/天）'), ('reservation_ev_surcharge', '预约充电桩附加费（元/单）'), ('grace_entry', '入场宽限期（分钟）'), ('grace_exit', '出场宽限期（分钟）'), ('monthly_commute', '月卡-通勤版'), ('monthly_premium', '月卡-高级版')], max_length=32, unique=True, verbose_name='费率类型'),
        ),
        migrations.RunPython(seed_reservation_pricing_rules, migrations.RunPython.noop),
    ]
