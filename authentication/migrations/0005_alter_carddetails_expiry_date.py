# Generated by Django 5.1.4 on 2025-01-01 07:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0004_usersubscription'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carddetails',
            name='expiry_date',
            field=models.CharField(max_length=7),
        ),
    ]
