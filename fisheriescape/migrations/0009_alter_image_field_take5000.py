# Generated by Django 3.2.5 on 2021-11-24 19:20

from django.db import migrations, models
import fisheriescape.models


class Migration(migrations.Migration):

    dependencies = [
        ('fisheriescape', '0008_alter_file_field_again'),
    ]

    operations = [
        migrations.AlterField(
            model_name='analyses',
            name='image',
            field=models.FileField(default='/fisheriescape/default_image.png', upload_to=fisheriescape.models.image_directory_path, verbose_name='image'),
        ),
    ]
