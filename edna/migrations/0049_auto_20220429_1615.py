# Generated by Django 3.2.10 on 2022-04-29 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edna', '0048_auto_20220429_1428'),
    ]

    operations = [
        migrations.AddField(
            model_name='assay',
            name='units',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='Units for LOQ and LOD'),
        ),
        migrations.AlterField(
            model_name='assay',
            name='is_ipc',
            field=models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], default=False, verbose_name='is this assay being used as an IPC?'),
        ),
    ]
