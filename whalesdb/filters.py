from . import models
from django_filters import FilterSet


class FilterHydrophone(FilterSet):

    class Meta:
        model = models.EqhHydrophoneProperties
        fields = ['emm', 'eqh_range_max', 'eqh_range_min']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

