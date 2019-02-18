# Generated by Django 2.1.4 on 2019-02-18 15:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0029_auto_20190218_1036'),
    ]

    operations = [
        migrations.AddField(
            model_name='staff',
            name='funding_source',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, related_name='staff_members', to='projects.FundingSource', verbose_name='funding source'),
        ),
        migrations.AlterField(
            model_name='capitalcost',
            name='funding_source',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, related_name='capital_costs', to='projects.FundingSource', verbose_name='funding source'),
        ),
        migrations.AlterField(
            model_name='omcost',
            name='funding_source',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, related_name='om_costs', to='projects.FundingSource', verbose_name='funding source'),
        ),
    ]
