# Generated by Django 3.2.14 on 2022-12-06 21:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herring', '0023_sample_egg_processing_complete'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sample',
            name='type',
            field=models.IntegerField(blank=True, choices=[(1, 'Port'), (2, 'Sea'), (3, 'Trap')], null=True, verbose_name='Sample type'),
        ),
    ]
