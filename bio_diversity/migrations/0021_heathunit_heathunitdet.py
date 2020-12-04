# Generated by Django 3.1.2 on 2020-12-04 13:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bio_diversity', '0020_auto_20201203_1549'),
    ]

    operations = [
        migrations.CreateModel(
            name='HeathUnit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='name (en)')),
                ('nom', models.CharField(blank=True, max_length=255, null=True, verbose_name='name (fr)')),
                ('description_en', models.TextField(blank=True, null=True, verbose_name='Description (en)')),
                ('description_fr', models.TextField(blank=True, null=True, verbose_name='Description (fr)')),
                ('created_by', models.CharField(max_length=32, verbose_name='Created By')),
                ('created_date', models.DateField(verbose_name='Created Date')),
                ('manufacturer', models.CharField(max_length=35, verbose_name='Maufacturer')),
                ('inservice_date', models.DateField(verbose_name='Date unit was put into service')),
                ('serial_number', models.CharField(max_length=50, verbose_name='Serial Number')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HeathUnitDet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('det_value', models.DecimalField(blank=True, decimal_places=5, max_digits=11, null=True, verbose_name='Value')),
                ('start_date', models.DateField(verbose_name='Date detail was recorded')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='Last Date Detail is valid')),
                ('det_valid', models.BooleanField(default='False', verbose_name='Detail still valid?')),
                ('comments', models.CharField(blank=True, max_length=2000, null=True, verbose_name='Comments')),
                ('created_by', models.CharField(max_length=32, verbose_name='Created By')),
                ('created_date', models.DateField(verbose_name='Created Date')),
                ('cdsc_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='bio_diversity.contdetsubjcode', verbose_name='Container Detail Subject Code')),
                ('contdc_id', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='bio_diversity.containerdetcode', verbose_name='Container Detail Code')),
                ('heat_id', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='bio_diversity.heathunit', verbose_name='HeathUnit')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
