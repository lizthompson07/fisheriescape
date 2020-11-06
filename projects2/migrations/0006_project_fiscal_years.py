# Generated by Django 3.1.2 on 2020-11-06 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shared_models', '0024_auto_20201102_1135'),
        ('projects2', '0005_project_staff_search_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='fiscal_years',
            field=models.ManyToManyField(editable=False, to='shared_models.FiscalYear'),
        ),
    ]
