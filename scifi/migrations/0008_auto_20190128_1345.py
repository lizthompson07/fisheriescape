# Generated by Django 2.1.4 on 2019-01-28 17:45

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('scifi', '0007_auto_20190128_1337'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ResponsibilityCentre',
            new_name='ResponsibilityCenter',
        ),
    ]
