# Generated by Django 3.2.4 on 2021-07-08 12:12

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bio_diversity', '0002_auto_20210621_0843'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='envtreatment',
            name='Environment_Treatment_Uniqueness',
        ),
        migrations.AddField(
            model_name='envtreatment',
            name='end_datetime',
            field=models.DateTimeField(blank=True, db_column='END', null=True, verbose_name='End date'),
        ),
        migrations.AddField(
            model_name='envtreatment',
            name='start_datetime',
            field=models.DateTimeField(db_column='START', default=datetime.datetime(2021, 7, 8, 9, 12, 31, 508892), verbose_name='Start date'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='individual',
            name='coll_id',
            field=models.ForeignKey(db_column='COLLECTION_ID', default=25, on_delete=django.db.models.deletion.CASCADE, to='bio_diversity.collection', verbose_name='Collection'),
        ),
        migrations.AlterField(
            model_name='sample',
            name='loc_id',
            field=models.ForeignKey(blank=True, db_column='LOCATION_ID', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='samples', to='bio_diversity.location', verbose_name='Location'),
        ),
        migrations.AddConstraint(
            model_name='envtreatment',
            constraint=models.UniqueConstraint(fields=('contx_id', 'envtc_id', 'start_datetime'), name='Environment_Treatment_Uniqueness'),
        ),
    ]
