from django.db import models


class CrsCruises(models.Model):
    crs_id = models.BigIntegerField(primary_key=True)
    crs_name = models.CharField(unique=True, max_length=50)
    crs_pi_name = models.CharField(max_length=50, blank=True, null=True)
    crs_institute_name = models.CharField(max_length=50, blank=True, null=True)
    crs_geographic_location = models.CharField(max_length=50, blank=True, null=True)
    crs_start_date = models.DateField(blank=True, null=True)
    crs_end_date = models.DateField(blank=True, null=True)
    crs_notes = models.CharField(max_length=4000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'crs_cruises'

    def __str__(self):
        return "{} : {} - {}".format(self.crs_name, self.crs_start_date, self.crs_end_date)


class DepDeployments(models.Model):
    dep_id = models.BigIntegerField(primary_key=True)
    dep_year = models.BigIntegerField()
    dep_month = models.BigIntegerField()
    dep_name = models.CharField(max_length=255)
    stn = models.ForeignKey('StnStations', models.DO_NOTHING)
    prj = models.ForeignKey('PrjProjects', models.DO_NOTHING)
    mor = models.ForeignKey('MorMooringSetups', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'dep_deployments'

    def __str__(self):
        return "{}".format(self.dep_name)


class EcaCalibrationEvent(models.Model):
    eca_id = models.BigIntegerField(primary_key=True)
    eca_date = models.DateField()
    eca_hydrophone = models.ForeignKey('EqpEquipment', models.DO_NOTHING, related_name='eca_hydrophone')
    eca_attachment = models.ForeignKey('EqpEquipment', models.DO_NOTHING, blank=True, null=True,
                                        related_name='eca_attachment')
    eca_notes = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'eca_calibration_event'


class EccCalibrationValue(models.Model):
    eca = models.ForeignKey(EcaCalibrationEvent, models.DO_NOTHING)
    ecc_frequency = models.DecimalField(max_digits=10, decimal_places=6)
    ecc_sensitivity = models.DecimalField(max_digits=10, decimal_places=6)

    class Meta:
        managed = False
        db_table = 'ecc_calibration_value'


class EcpChannelProperties(models.Model):
    ecp_id = models.BigIntegerField(primary_key=True)
    emm = models.ForeignKey('EmmMakeModel', models.DO_NOTHING)
    ecp_channel_no = models.BigIntegerField()
    eqa_adc_bits = models.ForeignKey('EqaAdcBitsCode', models.DO_NOTHING, db_column='eqa_adc_bits')
    ecp_voltage_range_min = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    ecp_voltage_range_max = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    ecp_gain = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ecp_channel_properties'
        unique_together = (('ecp_channel_no', 'emm'),)


class EdaEquipmentAttachments(models.Model):
    eda_id = models.BigIntegerField(primary_key=True)
    eqp = models.ForeignKey('EqpEquipment', models.DO_NOTHING)
    dep = models.ForeignKey(DepDeployments, models.DO_NOTHING)
    rec = models.ForeignKey('RecRecordingEvents', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'eda_equipment_attachments'


class EhaHydrophoneAttachments(models.Model):
    eha_id = models.BigIntegerField(primary_key=True)
    eda = models.ForeignKey(EdaEquipmentAttachments, models.DO_NOTHING)
    eqp = models.ForeignKey('EqpEquipment', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'eha_hydrophone_attachements'
        unique_together = (('eda', 'eqp'),)


class EmmMakeModel(models.Model):
    emm_id = models.BigIntegerField(primary_key=True)
    eqt = models.ForeignKey('EqtEquipmentTypeCode', models.DO_NOTHING)
    emm_make = models.CharField(max_length=50)
    emm_model = models.CharField(max_length=50)
    emm_depth_rating = models.BigIntegerField()
    emm_description = models.CharField(max_length=500)

    class Meta:
        managed = False
        db_table = 'emm_make_model'

    def __str__(self):
        return "{} {}".format(self.emm_make, self.emm_model)


class EprEquipmentParameters(models.Model):
    epr_id = models.BigIntegerField(primary_key=True)
    emm = models.ForeignKey(EmmMakeModel, models.DO_NOTHING)
    prm = models.ForeignKey('PrmParameterCode', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'epr_equipment_parameters'
        unique_together = (('emm', 'prm'),)


class EqaAdcBitsCode(models.Model):
    eqa_id = models.BigIntegerField(primary_key=True)
    eqa_name = models.CharField(unique=True, max_length=50)

    class Meta:
        managed = False
        db_table = 'eqa_adc_bits_code'

    def __str__(self):
        return "{}".format(self.eqa_name)


class EqhHydrophoneProperties(models.Model):
    emm = models.OneToOneField(EmmMakeModel, models.DO_NOTHING, primary_key=True)
    eqh_range_min = models.BigIntegerField()
    eqh_range_max = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'eqh_hydrophone_properties'


class EqpEquipment(models.Model):
    eqp_id = models.BigIntegerField(primary_key=True)
    emm = models.ForeignKey(EmmMakeModel, models.DO_NOTHING)
    eqp_serial = models.CharField(max_length=50)
    eqp_asset_id = models.CharField(unique=True, max_length=50)
    eqp_date_purchase = models.DateField()
    eqp_notes = models.CharField(max_length=4000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'eqp_equipment'

    def __str__(self):
        return "{} - {} - {}".format(self.emm, self.eqp_serial, self.eqp_asset_id)


class EqrRecorderProperties(models.Model):
    emm = models.OneToOneField(EmmMakeModel, models.DO_NOTHING, primary_key=True)
    eqc_max_channels = models.BigIntegerField()
    eqc_max_sample_rate = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'eqr_recorder_properties'


class EqtEquipmentTypeCode(models.Model):
    eqt_id = models.BigIntegerField(primary_key=True)
    eqt_name = models.CharField(unique=True, max_length=50)

    class Meta:
        managed = False
        db_table = 'eqt_equipment_type_code'

    def __str__(self):
        return "{}".format(self.eqt_name)


class MorMooringSetups(models.Model):
    mor_id = models.BigIntegerField(primary_key=True)
    mor_name = models.CharField(unique=True, max_length=50)
    mor_max_depth = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    mor_num_hydrophones = models.BigIntegerField(blank=True, null=True)
    mor_link_setup_image = models.CharField(max_length=4000, blank=True, null=True)
    mor_additional_equipment = models.CharField(max_length=4000, blank=True, null=True)
    mor_general_moor_description = models.CharField(max_length=4000, blank=True, null=True)
    more_notes = models.CharField(max_length=4000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mor_mooring_setups'

    def __str__(self):
        return "{}".format(self.mor_name)


class PrjProjects(models.Model):
    prj_id = models.BigIntegerField(primary_key=True)
    prj_name = models.CharField(unique=True, max_length=255)
    prj_description = models.CharField(max_length=4000, blank=True, null=True)
    prj_url = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'prj_projects'

    def __str__(self):
        return "{}".format(self.prj_name)


class PrmParameterCode(models.Model):
    prm_id = models.BigIntegerField(primary_key=True)
    prm_name = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'prm_parameter_code'

    def __str__(self):
        return "{}".format(self.prm_name)


class RecRecordingEvents(models.Model):
    rec_id = models.BigIntegerField(primary_key=True)
    rsc = models.ForeignKey('RscRecordingSchedules', models.DO_NOTHING)
    tea_id_setup_by = models.ForeignKey('TeaTeamMembers', models.DO_NOTHING, db_column='tea_id_setup_by', blank=True,
                                        null=True, related_name='tea_id_setup_by')
    rec_date_of_system_chk = models.DateField(blank=True, null=True)
    tea_id_checked_by = models.ForeignKey('TeaTeamMembers', models.DO_NOTHING, db_column='tea_id_checked_by',
                                          blank=True, null=True, related_name='tea_id_checked_by')
    rec_date_first_recording = models.DateField(blank=True, null=True)
    rec_date_last_recording = models.DateField(blank=True, null=True)
    rec_total_memory_used = models.BigIntegerField(blank=True, null=True)
    rec_hf_mem = models.BigIntegerField(blank=True, null=True)
    rec_lf_mem = models.BigIntegerField(blank=True, null=True)
    rec_date_data_download = models.DateField(blank=True, null=True)
    rec_data_store_url = models.CharField(max_length=255, blank=True, null=True)
    tea_id_downloaded_by = models.ForeignKey('TeaTeamMembers', models.DO_NOTHING, db_column='tea_id_downloaded_by',
                                             blank=True, null=True, related_name='tea_id_downloaded_by')
    rec_date_data_backed_up = models.DateField(blank=True, null=True)
    rec_data_backup_url = models.CharField(max_length=255, blank=True, null=True)
    tea_id_backed_up_by = models.ForeignKey('TeaTeamMembers', models.DO_NOTHING, db_column='tea_id_backed_up_by',
                                            blank=True, null=True, related_name='tea_id_backed_up_by')
    rec_channel_count = models.BigIntegerField(blank=True, null=True)
    rec_notes = models.CharField(max_length=4000, blank=True, null=True)
    rtt = models.ForeignKey('RttTimezoneCode', models.DO_NOTHING, blank=True, null=True)
    rec_first_in_water = models.DateField(blank=True, null=True)
    rec_last_in_water = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'rec_recording_events'


class RscRecordingSchedules(models.Model):
    rsc_id = models.BigIntegerField(primary_key=True)
    rsc_name = models.CharField(max_length=100, blank=True, null=True)
    rsc_period = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'rsc_recording_schedules'


class RstRecordingStage(models.Model):
    rst_id = models.BigIntegerField(primary_key=True)
    rst_channel_no = models.BigIntegerField(blank=True, null=True)
    rsc = models.ForeignKey(RscRecordingSchedules, models.DO_NOTHING)
    rst_active = models.CharField(max_length=1)
    rst_duration = models.BigIntegerField()
    rst_rate = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    rst_gain = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'rst_recording_stage'


class RttTimezoneCode(models.Model):
    rtt_id = models.BigIntegerField(primary_key=True)
    rtt_abb = models.CharField(max_length=5)
    rtt_name = models.CharField(max_length=50)
    rtt_offset = models.DecimalField(max_digits=4, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'rtt_timezone_code'


class SetStationEventCode(models.Model):
    set_id = models.BigIntegerField(primary_key=True)
    set_name = models.CharField(unique=True, max_length=50)
    set_description = models.CharField(max_length=400)

    class Meta:
        managed = False
        db_table = 'set_station_event_code'

    def __str__(self):
        return "{} - {}".format(self.set_name, self.set_description)


class SteStationEvents(models.Model):
    ste_id = models.BigIntegerField(primary_key=True)
    dep = models.ForeignKey(DepDeployments, models.DO_NOTHING)
    set_type = models.ForeignKey(SetStationEventCode, models.DO_NOTHING, db_column='set_type')
    ste_date = models.DateField()
    crs = models.ForeignKey(CrsCruises, models.DO_NOTHING)
    ste_lat_ship = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    ste_lon_ship = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    ste_depth_ship = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    ste_lat_mcal = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    ste_lon_mcal = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    ste_depth_mcal = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    ste_team = models.CharField(max_length=50, blank=True, null=True)
    ste_instrument_cond = models.CharField(max_length=4000, blank=True, null=True)
    ste_weather_cond = models.CharField(max_length=4000, blank=True, null=True)
    ste_logs = models.CharField(max_length=4000, blank=True, null=True)
    ste_notes = models.CharField(max_length=4000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ste_station_events'


class StnStations(models.Model):
    stn_id = models.BigIntegerField(primary_key=True)
    stn_name = models.CharField(max_length=100)
    stn_code = models.CharField(max_length=3)
    stn_revision = models.BigIntegerField()
    stn_planned_lat = models.DecimalField(max_digits=9, decimal_places=6)
    stn_planned_lon = models.DecimalField(max_digits=9, decimal_places=6)
    stn_planned_depth = models.DecimalField(max_digits=10, decimal_places=6)
    stn_notes = models.CharField(max_length=4000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'stn_stations'

    def __str__(self):
        current = "Past"

        list = StnStations.objects.filter(stn_name=self.stn_name).order_by("-stn_revision").values_list("stn_revision")

        if list[0][0] == self.stn_revision:
            current = "Current"

        return "{}: {} Revision {} ({})".format(self.stn_code, self.stn_name, self.stn_revision, current)


class TeaTeamMembers(models.Model):
    tea_id = models.BigIntegerField(primary_key=True)
    tea_abb = models.CharField(max_length=50, blank=True, null=True)
    tea_last_name = models.CharField(max_length=50)
    tea_first_name = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'tea_team_members'
        unique_together = (('tea_last_name', 'tea_first_name'),)

    def __str__(self):
        return "{}, {} ({})".format(self.tea_last_name, self.tea_first_name, self.tea_abb)