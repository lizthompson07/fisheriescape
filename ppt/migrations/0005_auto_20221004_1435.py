# Generated by Django 3.2.12 on 2022-10-04 17:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shared_models', '0031_subjectmatter_is_csas_request_tag'),
        ('ppt', '0004_pptadminuser_mode'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='csrf_fiscal_year',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='csrf_projects', to='shared_models.fiscalyear', verbose_name='CSRF application fiscal year'),
        ),
        migrations.AlterField(
            model_name='staff',
            name='is_primary_lead',
            field=models.BooleanField(choices=[(True, 'yes'), (False, 'no')], default=False, verbose_name='primary project contact'),
        ),
    ]
