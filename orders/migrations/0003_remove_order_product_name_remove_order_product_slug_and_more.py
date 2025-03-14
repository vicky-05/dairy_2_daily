# Generated by Django 5.1.4 on 2025-02-14 14:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_alter_order_options_alter_order_status'),
        ('products', '0011_remove_product_is_in_stock_product_quantity'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='product_name',
        ),
        migrations.RemoveField(
            model_name='order',
            name='product_slug',
        ),
        migrations.AddField(
            model_name='order',
            name='product',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='products.product'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='quantity',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
