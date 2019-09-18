from django_filters import FilterSet

from . import models
from . import forms


class GenericFilterSet(FilterSet):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        labels = forms.get_short_labels(self._meta.model)
        labels = forms.get_short_labels(self._meta.model)
        for key in labels.keys():
            self.filters[key].label = labels[key]


class EqrRecorder(GenericFilterSet):

    class Meta:
        model = models.EqrRecorderProperties
        fields = ['emm', 'eqc_max_channels', 'eqc_max_sample_rate']


class EqhHydrophone(GenericFilterSet):

    class Meta:
        model = models.EqhHydrophoneProperties
        fields = ['emm', 'eqh_range_max', 'eqh_range_min']


class FilterDeployments(GenericFilterSet):

    class Meta:
        model = models.DepDeployments
        fields = ['dep_year', 'dep_month', 'dep_name', 'stn', 'prj', 'mor', ]


class FilterCruises(GenericFilterSet):

    class Meta:
        model = models.CrsCruises
        fields = ['crs_name', 'crs_pi_name', 'crs_institute_name', 'crs_geographic_location', 'crs_start_date',
                  'crs_end_date', 'crs_notes', ]


class FilterMoorings(GenericFilterSet):

    class Meta:
        model = models.MorMooringSetups
        fields = ['mor_name', 'mor_max_depth', 'mor_num_hydrophones', 'mor_link_setup_image',
                  'mor_additional_equipment', 'mor_general_moor_description', 'more_notes', ]


class FilterStations(GenericFilterSet):

    class Meta:
        model = models.StnStations
        fields = ['stn_name', 'stn_code', 'stn_planned_lat', 'stn_planned_lon', 'stn_planned_depth', 'stn_notes', ]


class FilterStationEvents(GenericFilterSet):

    class Meta:
        model = models.SteStationEvents
        fields = ['dep', 'set_type', 'ste_date', 'crs', 'ste_lat_ship', 'ste_lon_ship', 'ste_depth_ship', 'ste_lat_mcal',
                  'ste_lon_mcal', 'ste_depth_mcal', 'ste_team', 'ste_instrument_cond', 'ste_weather_cond', 'ste_logs',
                  'ste_notes']


class FilterProjects(GenericFilterSet):

    class Meta:
        model = models.PrjProjects
        fields = ['prj_name', 'prj_descrption', 'prj_url', ]


class FilterRecordEvents(GenericFilterSet):

    class Meta:
        model = models.RecRecordingEvents
        fields = ['rsc', 'tea_id_setup_by', 'rec_date_of_system_chk', 'tea_id_checked_by', 'rec_date_first_recording',
                  'rec_date_last_recording', 'rec_total_memory_used', 'rec_hf_mem', 'rec_lf_mem',
                  'rec_date_data_download', 'rec_data_store_url', 'tea_id_downloaded_by', 'rec_date_data_backed_up',
                  'rec_data_backup_url', 'tea_id_backed_up_by', 'rec_channel_count', 'rec_notes', 'rtt',
                  'rec_first_in_water', 'rec_last_in_water', ]


class FilterRecordingSchedules(GenericFilterSet):

    class Meta:
        model = models.RscRecordingSchedules
        fields = ['rsc_name', 'rsc_period']


class FilterRecordingStages(GenericFilterSet):

    class Meta:
        model = models.RstRecordingStage
        fields = ['rst_channel_no', 'rsc', 'rst_active', 'rst_duration', 'rst_rate', 'rst_gain']
