# Generated by Django 3.2.12 on 2022-03-22 17:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fisheriescape', '0035_add_layerid_nafo_fix'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fishery',
            name='fishery_areas',
            field=models.ManyToManyField(related_name='fisherys', to='fisheriescape.FisheryArea', verbose_name='fishery areas'),
        ),
        migrations.AlterField(
            model_name='fishery',
            name='mitigation',
            field=models.ManyToManyField(blank=True, related_name='fisherys', to='fisheriescape.Mitigation', verbose_name='mitigation type'),
        ),
    ]
