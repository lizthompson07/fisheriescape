# Generated by Django 3.1.2 on 2021-01-12 19:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects2', '0009_auto_20210112_1035'),
    ]

    operations = [
        migrations.CreateModel(
            name='Collaboration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.IntegerField(choices=[(1, 'External Collaborator'), (2, 'Grant & Contribution Agreement'), (3, 'Collaborative Agreement')], verbose_name='collaboration type')),
                ('new_or_existing', models.IntegerField(choices=[(1, 'New'), (2, 'Existing')], verbose_name='new or existing')),
                ('organization', models.CharField(blank=True, max_length=1000, null=True, verbose_name='collaborating organization')),
                ('people', models.CharField(blank=True, max_length=1000, null=True, verbose_name='project lead(s)')),
                ('critical', models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], default=True, verbose_name='Critical to project delivery?')),
                ('agreement_title', models.CharField(blank=True, max_length=255, null=True, verbose_name='Title of the agreement (if applicable)')),
                ('gc_program', models.CharField(blank=True, max_length=255, null=True, verbose_name='Name of G&C program (if applicable)')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='notes')),
                ('project_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collaborations', to='projects2.projectyear', verbose_name='project year')),
            ],
            options={
                'ordering': ['type', 'organization'],
            },
        ),
    ]
