import logging
import django_filters
from django.utils.translation import gettext_lazy as _
from django_filters import FilterSet

from django.db.models import Q

from . import models


class multiTextFilter(django_filters.CharFilter):

    def filter(self, qs, value):
        qs = super().filter(qs, value)
        logging.debug("here")
        return qs


class ProjectFilter(FilterSet):

    t_and_a_filter = multiTextFilter(field_name='title', lookup_expr='icontains',
                                     label=_("Text & Abstract Filter"))

    class Meta:
        model = models.Project
        fields = [
            't_and_a_filter', 'theme', 'program_linkage', 'ecosystem_component', 'geographic_scope']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.filters['t_and_a_filter'].lookup_expr = 'icontains'
        self.filters['theme'].conjoined = True
        self.filters['program_linkage'].conjoined = True
