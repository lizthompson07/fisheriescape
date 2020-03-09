# Generated by Django 2.2.2 on 2020-02-27 15:53

from django.db import migrations, models
import django.db.models.deletion


def populate_mor_name(apps, schema_editor):
    MyModel = apps.get_model('whalesdb', 'MorMooringSetup')
    for row in MyModel.objects.all():
        row.mor_name = "mor_name_{}".format(row.mor_id)
        row.save(update_fields=['mor_name'])


class Migration(migrations.Migration):

    dependencies = [
        ('whalesdb', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_mor_name, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='stestationevent',
            name='dep',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='station_events', to='whalesdb.DepDeployment', verbose_name='Deployment'),
        ),
    ]
