# Generated by Django 3.2.16 on 2023-02-07 15:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trapnet', '0016_alter_specimen_age_type'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='electrofisher',
            options={'ordering': ['model_number']},
        ),
        migrations.RemoveField(
            model_name='electrofisher',
            name='nom',
        ),
        migrations.AddField(
            model_name='electrofisher',
            name='is_decommissioned',
            field=models.BooleanField(default=False, verbose_name='Decommissioned?'),
        ),
        migrations.AddField(
            model_name='electrofisher',
            name='notes',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='efsample',
            name='electrofisher',
            field=models.ForeignKey(blank=True, limit_choices_to={'is_decommissioned': False}, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='ef_samples', to='trapnet.electrofisher', verbose_name='electrofisher'),
        ),
        migrations.AlterField(
            model_name='electrofisher',
            name='model_number',
            field=models.CharField(default='test', max_length=255, verbose_name='model'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='electrofisher',
            name='name',
            field=models.CharField(max_length=255, unique=True, verbose_name='name'),
        ),
    ]
