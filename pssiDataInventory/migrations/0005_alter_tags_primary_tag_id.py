# Generated by Django 3.2.15 on 2022-12-16 23:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pssiDataInventory', '0004_auto_20221216_1504'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tags',
            name='primary_tag_ID',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
