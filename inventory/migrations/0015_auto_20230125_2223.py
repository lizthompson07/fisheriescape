# Generated by Django 3.2.16 on 2023-01-26 02:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('inventory', '0014_auto_20230125_1339'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='resource',
            name='paa_items',
        ),
        migrations.RemoveField(
            model_name='resource',
            name='people',
        ),
        migrations.AlterField(
            model_name='resource',
            name='last_modified_by',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='resource_last_modified_by_users', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='resourceperson',
            name='notes',
            field=models.TextField(blank=True, null=True, verbose_name='notes'),
        ),
        migrations.AlterField(
            model_name='resourceperson',
            name='role',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='inventory.personrole', verbose_name='role'),
        ),
        migrations.CreateModel(
            name='ResourcePerson2',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='notes')),
                ('organization', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='inventory.organization', verbose_name='affiliated organization')),
                ('resource', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='resource_people2', to='inventory.resource')),
                ('roles', models.ManyToManyField(blank=True, to='inventory.PersonRole', verbose_name='roles')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='resource_people', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['user'],
                'unique_together': {('resource', 'user')},
            },
        ),
        migrations.AddField(
            model_name='resource',
            name='users',
            field=models.ManyToManyField(through='inventory.ResourcePerson2', to=settings.AUTH_USER_MODEL),
        ),
    ]
