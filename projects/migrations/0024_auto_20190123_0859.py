# Generated by Django 2.1.4 on 2019-01-23 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0023_auto_20190118_1423'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='project',
            options={'ordering': ['-fiscal_year', 'section__division', 'section', 'project_title']},
        ),
        migrations.AddField(
            model_name='staff',
            name='overtime_description',
            field=models.FloatField(blank=True, default=0, null=True, verbose_name='overtime description'),
        ),
    ]
