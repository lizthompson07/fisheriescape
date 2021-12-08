# Generated by Django 3.2.5 on 2021-12-08 01:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scuba', '0032_auto_20211206_1344'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='transect',
            options={'ordering': ['region', 'name']},
        ),
        migrations.RemoveField(
            model_name='region',
            name='new_name',
        ),
        migrations.RemoveField(
            model_name='sample',
            name='region',
        ),
        migrations.RemoveField(
            model_name='sample',
            name='site',
        ),
        migrations.RemoveField(
            model_name='transect',
            name='site',
        ),
        migrations.AlterField(
            model_name='transect',
            name='old_name',
            field=models.CharField(blank=True, editable=False, max_length=255, null=True, verbose_name='old name'),
        ),
        migrations.DeleteModel(
            name='Site',
        ),
    ]
