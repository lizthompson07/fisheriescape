# Generated by Django 2.2.2 on 2020-05-12 23:26

from django.db import migrations, models
import django.db.models.deletion
import whalesdb.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('shared_models', '0004_auto_20200508_0049'),
    ]

    operations = [
        migrations.CreateModel(
            name='DepDeployment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dep_year', models.BigIntegerField(verbose_name='Year')),
                ('dep_month', models.BigIntegerField(verbose_name='Month')),
                ('dep_name', models.CharField(max_length=255, verbose_name='Deployment')),
            ],
        ),
        migrations.CreateModel(
            name='EcaCalibrationEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('eca_date', models.DateField(verbose_name='Calibration Date')),
                ('eca_notes', models.CharField(blank=True, max_length=50, null=True, verbose_name='Notes')),
            ],
        ),
        migrations.CreateModel(
            name='EdaEquipmentAttachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dep', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='attachments', to='whalesdb.DepDeployment', verbose_name='Deployment')),
            ],
        ),
        migrations.CreateModel(
            name='EmmMakeModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('emm_make', models.CharField(max_length=50, verbose_name='Make')),
                ('emm_model', models.CharField(max_length=50, verbose_name='Model')),
                ('emm_depth_rating', models.BigIntegerField(verbose_name='Depth Rating')),
                ('emm_description', models.CharField(max_length=500, verbose_name='Description')),
            ],
        ),
        migrations.CreateModel(
            name='EqaAdcBitsCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(blank=True, max_length=255, null=True)),
                ('description_en', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('description_fr', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='ADC Bit Name')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EqoOwner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(blank=True, max_length=255, null=True)),
                ('description_en', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('description_fr', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('name', models.CharField(max_length=100, verbose_name='Institute')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EqpEquipment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('eqp_serial', models.CharField(max_length=50, verbose_name='Serial Number')),
                ('eqp_asset_id', models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='Asset ID')),
                ('eqp_date_purchase', models.DateField(blank=True, null=True, verbose_name='Date Purchased')),
                ('eqp_notes', models.CharField(blank=True, max_length=4000, null=True, verbose_name='Notes')),
                ('eqp_retired', models.BooleanField(default=False, verbose_name='Retired?')),
                ('eqp_deployed', models.BooleanField(default=False, verbose_name='Deployed?')),
                ('emm', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='whalesdb.EmmMakeModel', verbose_name='Make and Model')),
                ('eqo_owned_by', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='whalesdb.EqoOwner', verbose_name='Owner')),
            ],
        ),
        migrations.CreateModel(
            name='EqtEquipmentTypeCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(blank=True, max_length=255, null=True)),
                ('description_en', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('description_fr', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='Equipment Type')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ErtRecorderType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(blank=True, max_length=255, null=True)),
                ('description_en', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('description_fr', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='Recorder Type')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MorMooringSetup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mor_name', models.CharField(max_length=50, unique=True, verbose_name='Name')),
                ('mor_max_depth', models.DecimalField(blank=True, decimal_places=6, max_digits=10, null=True, verbose_name='Max Depth')),
                ('mor_link_setup_image', models.CharField(blank=True, max_length=4000, null=True, verbose_name='Setup Image Link')),
                ('mor_setup_image', models.ImageField(blank=True, null=True, upload_to=whalesdb.models.mooring_directory_path, verbose_name='Setup Image')),
                ('mor_additional_equipment', models.TextField(blank=True, null=True, verbose_name='Equipment')),
                ('mor_general_moor_description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('mor_notes', models.TextField(blank=True, null=True, verbose_name='Notes')),
            ],
        ),
        migrations.CreateModel(
            name='PrjProject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(blank=True, max_length=255, null=True)),
                ('description_en', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('description_fr', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='Name')),
                ('prj_url', models.CharField(blank=True, max_length=255, null=True, verbose_name='URL')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PrmParameterCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(blank=True, max_length=255, null=True)),
                ('description_en', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('description_fr', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('name', models.CharField(blank=True, max_length=200, null=True, verbose_name='Parameter Code')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RecDataset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rec_start_date', models.DateField(blank=True, null=True, verbose_name='In Water Start Date')),
                ('rec_start_time', models.TimeField(blank=True, null=True, verbose_name='In Water Start Time')),
                ('rec_end_date', models.DateField(blank=True, null=True, verbose_name='In Water End Date')),
                ('rec_end_time', models.TimeField(blank=True, null=True, verbose_name='In Water End Time')),
                ('rec_backup_hd_1', models.IntegerField(blank=True, null=True, verbose_name='HD Backup 1')),
                ('rec_backup_hd_2', models.IntegerField(blank=True, null=True, verbose_name='HD Backup 2')),
                ('rec_notes', models.TextField(blank=True, null=True, verbose_name='Notes')),
                ('eda_id', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='whalesdb.EdaEquipmentAttachment', verbose_name='Equipment Deployment')),
            ],
        ),
        migrations.CreateModel(
            name='RetRecordingEventType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ret_name', models.CharField(max_length=50, verbose_name='Name')),
                ('ret_desc', models.CharField(max_length=255, verbose_name='Description')),
            ],
        ),
        migrations.CreateModel(
            name='RscRecordingSchedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rsc_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='Recording Schedule')),
                ('rsc_period', models.BigIntegerField(verbose_name='Period')),
            ],
        ),
        migrations.CreateModel(
            name='RttTimezoneCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rtt_abb', models.CharField(max_length=5, verbose_name='Abbreviation')),
                ('rtt_name', models.CharField(max_length=50, verbose_name='Name')),
                ('rtt_offset', models.DecimalField(decimal_places=2, max_digits=4, verbose_name='Offset')),
            ],
        ),
        migrations.CreateModel(
            name='SetStationEventCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(blank=True, max_length=255, null=True)),
                ('description_en', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('description_fr', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='Type')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EqhHydrophoneProperty',
            fields=[
                ('emm', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, related_name='hydrophone', serialize=False, to='whalesdb.EmmMakeModel', verbose_name='Hydrophone')),
                ('eqh_range_min', models.BigIntegerField(verbose_name='Min Range (dB)')),
                ('eqh_range_max', models.BigIntegerField(verbose_name='Max Range (db)')),
            ],
        ),
        migrations.CreateModel(
            name='TeaTeamMember',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tea_abb', models.CharField(blank=True, max_length=50, null=True, verbose_name='Abbreviation')),
                ('tea_last_name', models.CharField(max_length=50, verbose_name='Last Name')),
                ('tea_first_name', models.CharField(max_length=50, verbose_name='First Name')),
            ],
            options={
                'unique_together': {('tea_last_name', 'tea_first_name')},
            },
        ),
        migrations.CreateModel(
            name='StnStation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stn_name', models.CharField(max_length=100, verbose_name='Name')),
                ('stn_code', models.CharField(max_length=3, verbose_name='Code')),
                ('stn_revision', models.BigIntegerField(verbose_name='Revision')),
                ('stn_planned_lat', models.DecimalField(decimal_places=6, max_digits=9, verbose_name='Latitude')),
                ('stn_planned_lon', models.DecimalField(decimal_places=6, max_digits=9, verbose_name='Longitude')),
                ('stn_planned_depth', models.DecimalField(decimal_places=6, max_digits=10, verbose_name='Depth')),
                ('stn_notes', models.CharField(blank=True, max_length=4000, null=True, verbose_name='Notes')),
            ],
            options={
                'unique_together': {('stn_code', 'stn_revision')},
            },
        ),
        migrations.CreateModel(
            name='SteStationEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ste_date', models.DateField(verbose_name='Date')),
                ('ste_lat_ship', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True, verbose_name='Ship Latitude')),
                ('ste_lon_ship', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True, verbose_name='Ship Longitude')),
                ('ste_depth_ship', models.DecimalField(blank=True, decimal_places=6, max_digits=10, null=True, verbose_name='Ship Depth')),
                ('ste_lat_mcal', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True, verbose_name='MCAL Latitude')),
                ('ste_lon_mcal', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True, verbose_name='MCAL Longitude')),
                ('ste_depth_mcal', models.DecimalField(blank=True, decimal_places=6, max_digits=10, null=True, verbose_name='MCAL Depth')),
                ('ste_team', models.CharField(blank=True, max_length=50, null=True, verbose_name='Team')),
                ('ste_instrument_cond', models.CharField(blank=True, max_length=4000, null=True, verbose_name='Instrument Condition')),
                ('ste_weather_cond', models.CharField(blank=True, max_length=4000, null=True, verbose_name='Weather Conditions')),
                ('ste_logs', models.CharField(blank=True, max_length=4000, null=True, verbose_name='Log Location')),
                ('ste_notes', models.CharField(blank=True, max_length=4000, null=True, verbose_name='Notes')),
                ('crs', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='shared_models.Cruise', verbose_name='Cruise')),
                ('dep', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='station_events', to='whalesdb.DepDeployment', verbose_name='Deployment')),
                ('set_type', models.ForeignKey(db_column='set_type', on_delete=django.db.models.deletion.DO_NOTHING, to='whalesdb.SetStationEventCode', verbose_name='Event Type')),
            ],
        ),
        migrations.CreateModel(
            name='RstRecordingStage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rst_channel_no', models.BigIntegerField(blank=True, null=True, verbose_name='Channel Number')),
                ('rst_active', models.CharField(max_length=1, verbose_name='(A)ctive or (S)leep')),
                ('rst_duration', models.BigIntegerField(verbose_name='Duration')),
                ('rst_rate', models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True, verbose_name='Rate (Hz)')),
                ('rsc', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='stages', to='whalesdb.RscRecordingSchedule', verbose_name='Schedule')),
            ],
        ),
        migrations.CreateModel(
            name='ReeRecordingEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ree_date', models.DateField(verbose_name='Date')),
                ('ree_time', models.TimeField(blank=True, null=True, verbose_name='Time')),
                ('ree_notes', models.TextField(blank=True, null=True, verbose_name='Notes')),
                ('rec_id', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='whalesdb.RecDataset', verbose_name='Dataset')),
                ('ret_id', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='whalesdb.RetRecordingEventType', verbose_name='Event Type')),
                ('rtt_id', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='whalesdb.RttTimezoneCode', verbose_name='Timezone')),
                ('tea_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='whalesdb.TeaTeamMember', verbose_name='Team Member')),
            ],
        ),
        migrations.AddField(
            model_name='recdataset',
            name='rsc_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='whalesdb.RscRecordingSchedule', verbose_name='Recording Schedule'),
        ),
        migrations.AddField(
            model_name='recdataset',
            name='rtt_dataset',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='rtt_dataset', to='whalesdb.RttTimezoneCode', verbose_name='Dataset Timezone'),
        ),
        migrations.AddField(
            model_name='recdataset',
            name='rtt_in_water',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='rtt_in_water', to='whalesdb.RttTimezoneCode', verbose_name='In Water Timezone'),
        ),
        migrations.CreateModel(
            name='RciChannelInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rci_name', models.CharField(blank=True, max_length=30, null=True, verbose_name='Name')),
                ('rci_size', models.IntegerField(blank=True, null=True, verbose_name='Size (GB)')),
                ('rci_gain', models.IntegerField(blank=True, null=True, verbose_name='Gain')),
                ('rci_volts', models.DecimalField(blank=True, decimal_places=1, max_digits=4, null=True, verbose_name='Voltage')),
                ('rec_id', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='whalesdb.RecDataset', verbose_name='Dataset')),
            ],
        ),
        migrations.CreateModel(
            name='EtrTechnicalRepairEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('etr_date', models.DateField(blank=True, null=True, verbose_name='Date')),
                ('etr_issue_desc', models.TextField(blank=True, null=True, verbose_name='Issue')),
                ('etr_repair_desc', models.TextField(blank=True, null=True, verbose_name='Repair')),
                ('etr_repaired_by', models.CharField(blank=True, max_length=50, null=True, verbose_name='Repaired By')),
                ('eqp_id', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='whalesdb.EqpEquipment', verbose_name='Equipment')),
            ],
        ),
        migrations.AddField(
            model_name='emmmakemodel',
            name='eqt',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='whalesdb.EqtEquipmentTypeCode', verbose_name='Equipment Type'),
        ),
        migrations.AddField(
            model_name='edaequipmentattachment',
            name='eqp',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='deployments', to='whalesdb.EqpEquipment', verbose_name='Equipment'),
        ),
        migrations.CreateModel(
            name='EccCalibrationValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ecc_frequency', models.DecimalField(decimal_places=6, max_digits=10, verbose_name='Frequency')),
                ('ecc_sensitivity', models.DecimalField(decimal_places=6, max_digits=10, verbose_name='Sensitivity')),
                ('eca', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='whalesdb.EcaCalibrationEvent', verbose_name='Calibration Event')),
            ],
        ),
        migrations.AddField(
            model_name='ecacalibrationevent',
            name='eca_attachment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='eca_attachment', to='whalesdb.EqpEquipment', verbose_name='Equipment'),
        ),
        migrations.AddField(
            model_name='ecacalibrationevent',
            name='eca_hydrophone',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='eca_hydrophone', to='whalesdb.EqpEquipment', verbose_name='Hydrophone'),
        ),
        migrations.AddField(
            model_name='depdeployment',
            name='mor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='moorings', to='whalesdb.MorMooringSetup', verbose_name='Mooring Setup'),
        ),
        migrations.AddField(
            model_name='depdeployment',
            name='prj',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='projects', to='whalesdb.PrjProject', verbose_name='Project'),
        ),
        migrations.AddField(
            model_name='depdeployment',
            name='stn',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='stations', to='whalesdb.StnStation', verbose_name='Station'),
        ),
        migrations.CreateModel(
            name='EqrRecorderProperties',
            fields=[
                ('emm', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='recorder', serialize=False, to='whalesdb.EmmMakeModel', verbose_name='Make and Model')),
                ('eqr_internal_hydro', models.BooleanField(default=False, verbose_name='Has Internal Hydrophone')),
                ('ert', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='whalesdb.ErtRecorderType', verbose_name='Recorder Type')),
            ],
        ),
        migrations.CreateModel(
            name='EprEquipmentParameter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('emm', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='whalesdb.EmmMakeModel', verbose_name='Equipment')),
                ('prm', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='whalesdb.PrmParameterCode', verbose_name='Parameter')),
            ],
            options={
                'unique_together': {('emm', 'prm')},
            },
        ),
        migrations.CreateModel(
            name='EhaHydrophoneAttachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('eda', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='whalesdb.EdaEquipmentAttachment', verbose_name='Attachment')),
                ('eqp', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='whalesdb.EqpEquipment', verbose_name='Hydrophone')),
            ],
            options={
                'unique_together': {('eda', 'eqp')},
            },
        ),
        migrations.CreateModel(
            name='EcpChannelProperty',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ecp_channel_no', models.BigIntegerField(verbose_name='Channel Number')),
                ('ecp_voltage_range_min', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, verbose_name='Maximum voltage')),
                ('ecp_voltage_range_max', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, verbose_name='Minimum voltage')),
                ('eqa_adc_bits', models.ForeignKey(db_column='eqa_adc_bits', on_delete=django.db.models.deletion.DO_NOTHING, to='whalesdb.EqaAdcBitsCode', verbose_name='ADC Bits')),
                ('eqr', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='channels', to='whalesdb.EqrRecorderProperties', verbose_name='Recorder')),
            ],
            options={
                'unique_together': {('ecp_channel_no', 'eqr')},
            },
        ),
    ]
