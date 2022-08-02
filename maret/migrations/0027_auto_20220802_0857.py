# Generated by Django 3.2.12 on 2022-08-02 11:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maret', '0026_remove_contactextension_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='interaction',
            name='is_committee',
            field=models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], default=False, verbose_name='Committee or Working Group'),
        ),
        migrations.AlterField(
            model_name='interaction',
            name='interaction_type',
            field=models.IntegerField(blank=True, choices=[(10, 'Email or other written correspondence '), (11, 'In-person meeting'), (12, 'Hybrid meeting'), (13, 'Virtual or phone meeting '), (14, 'Conference or workshop ')], default=None, null=True),
        ),
    ]
