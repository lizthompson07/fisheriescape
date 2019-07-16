from django.utils.translation import gettext_lazy as _
from django_filters import FilterSet

from . import models
from . import forms


class EquipmentFilterSet(FilterSet):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        labels = forms.get_short_labels(self._meta.model)
        for key in labels.keys():
            self.filters[key].label = labels[key]


class FilterRecorder(EquipmentFilterSet):

    class Meta:
        model = models.EqrRecorderProperties
        fields = ['emm', 'eqc_max_channels', 'eqc_max_sample_rate']


class FilterHydrophone(EquipmentFilterSet):

    class Meta:
        model = models.EqhHydrophoneProperties
        fields = ['emm', 'eqh_range_max', 'eqh_range_min']

