# Generated by Django 5.1.4 on 2025-03-07 13:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0012_alter_product_subscription_plan'),
        ('subscriptions', '0003_alter_subscriptionplan_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='subscription_plan',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='subscriptions.subscriptionplan'),
        ),
    ]
