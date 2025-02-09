# Generated by Django 5.1.4 on 2025-02-02 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0012_securityquestion'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='profile_picture',
            field=models.ImageField(blank=True, default='profile_pics/default_profile.png', help_text='User profile picture', null=True, upload_to='profile_pics/'),
        ),
    ]
