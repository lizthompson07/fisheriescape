# Generated by Django 3.2.4 on 2021-10-26 14:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('res', '0030_auto_20211026_1138'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recommendation',
            name='application',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='recommendation', to='res.application'),
        ),
    ]
