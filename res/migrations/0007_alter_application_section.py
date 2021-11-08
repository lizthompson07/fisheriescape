# Generated by Django 3.2.4 on 2021-10-13 11:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shared_models', '0028_alter_organization_uuid'),
        ('res', '0006_application_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='section',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='res_applications', to='shared_models.section', verbose_name='DFO Section'),
        ),
    ]
