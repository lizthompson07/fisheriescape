from django_filters import FilterSet

from . import models
from . import forms


class GenericFilterSet(FilterSet):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        labels = forms.get_short_labels(self._meta.model)
        for key in labels.keys():
            self.filters[key].label = labels[key]


class FilterRecorder(GenericFilterSet):

    class Meta:
        model = models.EqrRecorderProperties
        fields = ['emm', 'eqc_max_channels', 'eqc_max_sample_rate']


class FilterHydrophone(GenericFilterSet):

    class Meta:
        model = models.EqhHydrophoneProperties
        fields = ['emm', 'eqh_range_max', 'eqh_range_min']


class FilterDeployments(GenericFilterSet):

    class Meta:
        model = models.DepDeployments
        fields = ['dep_name', 'stn', 'prj', 'mor', ]


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
        fields = ['stn_name', 'stn_planned_lat', 'stn_planned_lon', 'stn_planned_depth', 'stn_notes', ]


class FilterProjects(GenericFilterSet):

    class Meta:
        model = models.PrjProjects
        fields = ['prj_name', 'prj_descrption', 'prj_url', ]


class FilterRecordEvent(GenericFilterSet):

    class Meta:
        model = models.RecRecordingEvents
        fields = ['tea_id_setup_by', 'rec_date_of_system_chk', 'tea_id_checked_by', 'rec_date_first_recording',
                  'rec_date_last_recording', 'rec_total_memory_used', 'rec_hf_mem', 'rec_lf_mem',
                  'rec_date_data_download', 'rec_data_store_url', 'tea_id_downloaded_by', 'rec_date_data_backed_up',
                  'rec_data_backup_url', 'tea_id_backed_up_by', 'rec_channel_count', 'rec_notes', 'rtt',
                  'rec_first_in_water', 'rec_last_in_water', ]
