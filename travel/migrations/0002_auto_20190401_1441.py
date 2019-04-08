# Generated by Django 2.1.4 on 2019-04-01 17:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('travel', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='fiscal_year',
            field=models.ForeignKey(blank=True, default=2020, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='shared_models.FiscalYear', verbose_name='fiscal year'),
        ),
    ]
