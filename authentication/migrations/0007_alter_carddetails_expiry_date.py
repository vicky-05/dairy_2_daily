# Generated by Django 5.1.4 on 2025-01-01 12:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0006_remove_carddetails_card_number_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carddetails',
            name='expiry_date',
            field=models.CharField(max_length=7),
        ),
    ]
