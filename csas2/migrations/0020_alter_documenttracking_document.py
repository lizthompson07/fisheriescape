# Generated by Django 3.2 on 2021-04-28 17:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('csas2', '0019_auto_20210428_1411'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documenttracking',
            name='document',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='tracking', to='csas2.document'),
        ),
    ]
