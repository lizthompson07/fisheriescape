# Generated by Django 3.2.16 on 2023-01-25 18:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shared_models', '0036_person_org_from_inventory'),
        ('inventory', '0015_auto_20230125_1347'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='resource',
            name='paa_items',
        ),
        migrations.AlterField(
            model_name='resource',
            name='last_modified_by',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='resource',
            name='people',
            field=models.ManyToManyField(through='inventory.ResourcePerson2', to='shared_models.Person'),
        ),
    ]
