# Generated by Django 3.2.4 on 2021-09-24 12:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spot', '0004_auto_20210401_0824'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='appendix_k',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
