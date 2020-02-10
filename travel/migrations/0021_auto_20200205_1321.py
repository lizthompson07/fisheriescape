# Generated by Django 2.2.2 on 2020-02-05 17:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('travel', '0020_auto_20200205_1201'),
    ]

    operations = [
        migrations.AddField(
            model_name='conference',
            name='is_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='conference',
            name='verified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='trips_verified_by', to=settings.AUTH_USER_MODEL),
        ),
    ]
