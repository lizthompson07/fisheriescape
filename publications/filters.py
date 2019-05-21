import django_filters
from django_filters import FilterSet
from publications import models
import datetime


class PublicationsFilter(FilterSet):

    class Meta:
        model = models.Publications
        fields = [
            'pub_year', 'pub_title', 'theme', 'program_linkage', 'ecosystem_component']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        dates = [(d, d.year) for d in
                 models.Publications.objects.order_by().values_list('pub_year', flat=True).distinct()]

        self.filters['pub_title'].lookup_expr = 'icontains'

        self.filters['pub_year'] = django_filters.ChoiceFilter(field_name='pub_year', lookup_expr='exact',
                                                               choices=dates)

        self.filters['theme'].conjoined = True
        self.filters['program_linkage'].conjoined = True
