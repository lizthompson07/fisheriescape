import django_filters
from django_filters import rest_framework as filters
from rest_framework import generics
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework import viewsets
from rest_framework import mixins

from rest_framework_gis.filters import GeometryFilter
from rest_framework_gis.filterset import GeoFilterSet
from .serializers import ScoreSerializer, ScoreFeatureSerializer
from .. import models


# class EntryCSVAPIView(ListAPIView):
#     renderer_classes = [CSVRenderer]
#     serializer_class = serializers.EntrySerializer
#     permission_classes = [permissions.IsAuthenticatedOrReadOnly]
#     queryset = models.Entry.objects.all()


#have to have filters.Filterset also because otherwise crispy-forms doesn't have submit button
# see https://github.com/encode/django-rest-framework/issues/3636

class MyFilter(GeoFilterSet, filters.FilterSet):
    # hexagon = GeometryFilter(field_name='hexagon', lookup_expr='contains')

    class Meta:
        model = models.Score
        fields = ['species', 'week']


## for nested relationship

# class ScoreViewSet(ReadOnlyModelViewSet):
#     queryset = models.Hexagon.objects.all()
#     serializer_class = HexagonSerializer


class ScoreViewSet(ModelViewSet):
    queryset = models.Score.objects.all()
    serializer_class = ScoreSerializer
    lookup_field = "id"  # change this to slug eventually?
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, )
    filterset_class = MyFilter
    search_fields = ['species__english_name', 'species__french_name', 'week__week_number']


class ScoreFeatureViewSet(ModelViewSet):
    queryset = models.Score.objects.all()
    serializer_class = ScoreFeatureSerializer

# For TESTING
# class ScoreViewSet(ModelViewSet):
#     queryset = models.Species.objects.all()
#     serializer_class = ScoreSerializer
#     filter_backends = (filters.DjangoFilterBackend,)
#     filterset_fields = ('english_name', 'french_name')

# class ScoreListView(mixins.UpdateModelMixin,
#                      mixins.ListModelMixin,
#                      mixins.RetrieveModelMixin,
#                      viewsets.GenericViewSet):
#     queryset = models.Score.objects.all()
#     serializer_class = ScoreSerializer
#     filter_backends = [SearchFilter]
#     # filter_class = MyFilter
#     search_fields = ['species', 'site_score']
#     # filterset_fields = ['species', 'hexagon__grid_id']