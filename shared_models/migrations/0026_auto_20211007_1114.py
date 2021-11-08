# Generated by Django 3.2.4 on 2021-10-07 14:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shared_models', '0025_auto_20211007_1109'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cruise',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='cruise',
            name='probe',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='shared_models.probe'),
        ),
    ]
