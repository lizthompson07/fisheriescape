from django_filters import FilterSet

from . import models
from . import forms

from django.db.models.base import ModelBase


class GenericFilterSet(FilterSet):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        labels = forms.get_short_labels(self._meta.model)
        try:
            for key in labels.keys():
                if key in self.filters.keys():
                    self.filters[key].label = labels[key]
        except KeyError:
            print("Label for key '" + key + "' not found in object '" + str(self._meta.model) + "'")
            print("Filters: " + str(self.filters))


class CrsFilter(GenericFilterSet):

    class Meta:
        model = models.CrsCruise
        fields = ['crs_name', 'crs_pi_name', 'crs_institute_name', 'crs_geographic_location', 'crs_start_date',
                  'crs_end_date', 'crs_notes', ]


class DepFilter(GenericFilterSet):

    class Meta:
        model = models.DepDeployment
        fields = ['dep_year', 'dep_month', 'dep_name', 'stn', 'prj', 'mor', ]


class EdaFilter(GenericFilterSet):

    class Meta:
        model = models.EdaEquipmentAttachment
        fields = ['eqp', 'dep', 'rec']


class EdhFilter(GenericFilterSet):

    class Meta:
        model = models.EhaHydrophoneAttachment
        fields = ['eda', 'eqp',]


class EmmFilter(GenericFilterSet):

    class Meta:
        model = models.EmmMakeModel
        fields = ['emm_make', 'emm_model', 'emm_depth_rating']


class EqhFilter(GenericFilterSet):

    class Meta:
        model = models.EqhHydrophoneProperty
        fields = ['emm', 'eqh_range_max', 'eqh_range_min']


class EqpFilter(GenericFilterSet):

    class Meta:
        model = models.EqpEquipment
        fields = ['emm', 'eqp_serial', 'eqp_date_purchase', 'eqp_asset_id', 'eqp_notes']


class EtrTechnicalRepairEvent(GenericFilterSet):

    class Meta:
        model = models.EtrTechnicalRepairEvent
        fields = ['eqp_id', 'etr_date', ]


class MorFilter(GenericFilterSet):

    class Meta:
        model = models.MorMooringSetup
        fields = ['mor_name', 'mor_max_depth', 'mor_link_setup_image',
                  'mor_additional_equipment', 'mor_general_moor_description', 'more_notes', ]


class PrjFilter(GenericFilterSet):

    class Meta:
        model = models.PrjProject
        fields = ['prj_name', 'prj_description', 'prj_url', ]


class RecFilter(GenericFilterSet):

    class Meta:
        model = models.RecRecordingEvent
        fields = ['rsc', 'tea_id_setup_by', 'rec_date_of_system_chk', 'tea_id_checked_by', 'rec_date_first_recording',
                  'rec_date_last_recording', 'rec_total_memory_used', 'rec_hf_mem', 'rec_lf_mem',
                  'rec_date_data_download', 'rec_data_store_url', 'tea_id_downloaded_by', 'rec_date_data_backed_up',
                  'rec_data_backup_url', 'tea_id_backed_up_by', 'rec_channel_count', 'rec_notes', 'rtt',
                  'rec_first_in_water', 'rec_last_in_water', 'rec_lf_channel_gain', 'rec_lf_channel_volts',
                  'rec_hf_channel_gain', 'rec_hf_channel_volts']


class RscFilter(GenericFilterSet):

    class Meta:
        model = models.RscRecordingSchedule
        fields = ['rsc_name', 'rsc_period']


class RstFilter(GenericFilterSet):

    class Meta:
        model = models.RstRecordingStage
        fields = ['rst_channel_no', 'rsc', 'rst_active', 'rst_duration', 'rst_rate']


class SteFilter(GenericFilterSet):

    class Meta:
        model = models.SteStationEvent
        fields = ['dep', 'set_type', 'ste_date', 'crs', 'ste_lat_ship', 'ste_lon_ship', 'ste_depth_ship', 'ste_lat_mcal',
                  'ste_lon_mcal', 'ste_depth_mcal', 'ste_team', 'ste_instrument_cond', 'ste_weather_cond', 'ste_logs',
                  'ste_notes']


class StnFilter(GenericFilterSet):

    class Meta:
        model = models.StnStation
        fields = ['stn_name', 'stn_code', 'stn_revision', 'stn_planned_lat', 'stn_planned_lon', 'stn_planned_depth', 'stn_notes', ]
