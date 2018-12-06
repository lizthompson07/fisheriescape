# Generated by Django 2.0.4 on 2018-12-06 19:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('camp', '0027_auto_20181121_1216'),
    ]

    operations = [
        migrations.AddField(
            model_name='species',
            name='sav',
            field=models.BooleanField(default=False, verbose_name='Submerged aquatic vegetation (SAV)'),
        ),
    ]
