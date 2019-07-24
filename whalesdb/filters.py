from django.utils.translation import gettext_lazy as _
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


class FilterRecordEvent(GenericFilterSet):

    class Meta:
        model = models.RecRecordingEvents
        fields = ['tea_id_setup_by', 'rec_date_of_system_chk', 'tea_id_checked_by', 'rec_date_first_recording',
                  'rec_date_last_recording', 'rec_total_memory_used', 'rec_hf_mem', 'rec_lf_mem',
                  'rec_date_data_download', 'rec_data_store_url', 'tea_id_downloaded_by', 'rec_date_data_backed_up',
                  'rec_data_backup_url', 'tea_id_backed_up_by', 'rec_channel_count', 'rec_notes', 'rtt',
                  'rec_first_in_water', 'rec_last_in_water', ]
