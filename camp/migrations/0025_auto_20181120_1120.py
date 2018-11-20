# Generated by Django 2.0.4 on 2018-11-20 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('camp', '0024_auto_20181120_1036'),
    ]

    operations = [
        migrations.AlterField(
            model_name='speciesobservation',
            name='adults',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='speciesobservation',
            name='unknown',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='speciesobservation',
            name='yoy',
            field=models.FloatField(blank=True, null=True, verbose_name='young of the year'),
        ),
    ]
