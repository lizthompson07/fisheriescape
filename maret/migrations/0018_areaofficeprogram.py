# Generated by Django 3.2.12 on 2022-04-26 12:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('maret', '0017_auto_20220419_1131'),
    ]

    operations = [
        migrations.CreateModel(
            name='AreaOfficeProgram',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='name (en)')),
                ('nom', models.CharField(blank=True, max_length=255, null=True, verbose_name='name (fr)')),
                ('area_office', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='maret.areaoffice', verbose_name='Area Office Program')),
            ],
            options={
                'ordering': ['name'],
                'abstract': False,
            },
        ),
    ]
