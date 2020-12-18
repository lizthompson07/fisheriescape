# Generated by Django 3.1.2 on 2020-12-18 17:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bio_diversity', '0070_protocol_evntc_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='perc_id',
            field=models.ForeignKey(limit_choices_to={'perc_valid': True}, on_delete=django.db.models.deletion.DO_NOTHING, to='bio_diversity.personnelcode', verbose_name='Personnel Code'),
        ),
        migrations.AlterField(
            model_name='event',
            name='prog_id',
            field=models.ForeignKey(limit_choices_to={'valid': True}, on_delete=django.db.models.deletion.DO_NOTHING, to='bio_diversity.program', verbose_name='Program'),
        ),
        migrations.AlterField(
            model_name='individual',
            name='grp_id',
            field=models.ForeignKey(blank=True, limit_choices_to={'grp_valid': True}, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='bio_diversity.group', verbose_name='From Parent Group'),
        ),
        migrations.AlterField(
            model_name='pairing',
            name='indv_id',
            field=models.ForeignKey(limit_choices_to={'indv_valid': True, 'ufid__isnull': False}, on_delete=django.db.models.deletion.DO_NOTHING, to='bio_diversity.individual', verbose_name='Dam'),
        ),
        migrations.AlterField(
            model_name='protocol',
            name='prog_id',
            field=models.ForeignKey(limit_choices_to={'valid': True}, on_delete=django.db.models.deletion.DO_NOTHING, to='bio_diversity.program', verbose_name='Program'),
        ),
        migrations.AlterField(
            model_name='protofile',
            name='prot_id',
            field=models.ForeignKey(limit_choices_to={'valid': True}, on_delete=django.db.models.deletion.DO_NOTHING, related_name='protf_id', to='bio_diversity.protocol', verbose_name='Protocol'),
        ),
        migrations.AlterField(
            model_name='sire',
            name='indv_id',
            field=models.ForeignKey(limit_choices_to={'indv_valid': True, 'ufid__isnull': False}, on_delete=django.db.models.deletion.DO_NOTHING, to='bio_diversity.individual', verbose_name='Sire UFID'),
        ),
        migrations.AlterField(
            model_name='sire',
            name='pair_id',
            field=models.ForeignKey(limit_choices_to={'valid': True}, on_delete=django.db.models.deletion.DO_NOTHING, related_name='sire', to='bio_diversity.pairing', verbose_name='Pairing'),
        ),
        migrations.AlterField(
            model_name='spawning',
            name='pair_id',
            field=models.ForeignKey(limit_choices_to={'valid': True}, on_delete=django.db.models.deletion.DO_NOTHING, to='bio_diversity.pairing', verbose_name='Pairing'),
        ),
        migrations.AlterField(
            model_name='team',
            name='perc_id',
            field=models.ForeignKey(limit_choices_to={'perc_valid': True}, on_delete=django.db.models.deletion.DO_NOTHING, to='bio_diversity.personnelcode', verbose_name='Team Member'),
        ),
    ]
