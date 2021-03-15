# Generated by Django 3.1.2 on 2021-03-15 13:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('edna', '0007_auto_20210315_1019'),
    ]

    operations = [
        migrations.AlterField(
            model_name='filter',
            name='created_by',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='filter_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='filter',
            name='updated_by',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='filter_updated_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='pcr',
            name='created_by',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='pcr_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='pcr',
            name='updated_by',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='pcr_updated_by', to=settings.AUTH_USER_MODEL),
        ),
    ]
