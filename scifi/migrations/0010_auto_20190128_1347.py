# Generated by Django 2.1.4 on 2019-01-28 17:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scifi', '0009_auto_20190128_1347'),
    ]

    operations = [
        migrations.RenameField(
            model_name='responsibilitycenter',
            old_name='names',
            new_name='name',
        ),
    ]
