# Generated by Django 3.2.2 on 2021-06-14 15:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import trapnet.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('trapnet', '0012_alter_riversite_river'),
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('caption', models.CharField(max_length=255)),
                ('image', models.ImageField(upload_to=trapnet.models.file_directory_path)),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='file_created_by', to=settings.AUTH_USER_MODEL)),
                ('observation', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='files', to='trapnet.observation')),
                ('updated_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='file_updated_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['caption'],
            },
        ),
    ]
