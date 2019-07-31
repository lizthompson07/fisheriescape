# Generated by Django 2.2.2 on 2019-07-31 18:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sar_search', '0011_auto_20190731_1321'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='range',
            name='county',
        ),
        migrations.AlterField(
            model_name='rangepoints',
            name='latitude_n',
            field=models.FloatField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='rangepoints',
            name='longitude_w',
            field=models.FloatField(default=1),
            preserve_default=False,
        ),
    ]
