# Generated by Django 3.2.16 on 2023-01-23 14:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('edna', '0006_auto_20230123_0924'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sample',
            name='sample_batch',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='samples', to='edna.samplebatch', verbose_name='sample collection / receipt'),
        ),
        migrations.AlterField(
            model_name='samplebatch',
            name='operators',
            field=models.ManyToManyField(blank=True, to='edna.ednaUser', verbose_name='Received by'),
        ),
        migrations.AlterField(
            model_name='samplebatch',
            name='sent_by',
            field=models.CharField(blank=True, max_length=100, verbose_name='Received from'),
        ),
    ]
