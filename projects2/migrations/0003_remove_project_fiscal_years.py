# Generated by Django 3.1.2 on 2020-12-03 14:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects2', '0002_auto_20201203_1015'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='fiscal_years',
        ),
    ]
