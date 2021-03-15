# Generated by Django 3.1.2 on 2021-03-15 19:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spot', '0014_auto_20210315_1144'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='person',
            name='organization',
        ),
        migrations.AddField(
            model_name='person',
            name='organization',
            field=models.ManyToManyField(blank=True, default=None, null=True, to='spot.Organization', verbose_name='organization'),
        ),
    ]
