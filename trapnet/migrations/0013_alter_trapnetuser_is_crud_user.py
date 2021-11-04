# Generated by Django 3.2.5 on 2021-11-04 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trapnet', '0012_auto_20211104_1015'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trapnetuser',
            name='is_crud_user',
            field=models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], default=False, verbose_name='CRUD only?'),
        ),
    ]
