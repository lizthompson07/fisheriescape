import json
import time
import django_filters
from django_filters import rest_framework as filters
from rest_framework import generics
from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework import viewsets
from rest_framework import mixins

from rest_framework_gis.filters import GeometryFilter
from rest_framework_gis.filterset import GeoFilterSet
from . import pagination
from .serializers import ScoreSerializer, ScoreFeatureSerializer, SpeciesSerializer, WeekSerializer, HexagonSerializer
from .. import models


# class EntryCSVAPIView(ListAPIView):
#     renderer_classes = [CSVRenderer]
#     serializer_class = serializers.EntrySerializer
#     permission_classes = [permissions.IsAuthenticatedOrReadOnly]
#     queryset = models.Entry.objects.all()


# have to have filters.Filterset also because otherwise crispy-forms doesn't have submit button
# see https://github.com/encode/django-rest-framework/issues/3636

# class MyFilter(GeoFilterSet, filters.FilterSet):
#     # hexagon = GeometryFilter(field_name='hexagon', lookup_expr='contains')
#
#     class Meta:
#         model = models.Score
#         fields = ['id', 'species', 'week']

# class MyHexFilter(GeoFilterSet, filters.FilterSet):
#     # hexagon = GeometryFilter(field_name='hexagon', lookup_expr='contains')
#
#     class Meta:
#         model = models.Hexagon
#         fields = ['id', 'scores__species', 'scores__week']
#
#
# ## for nested relationship
#
# class ScoreViewSet(ReadOnlyModelViewSet):
#     queryset = models.Hexagon.objects.all()
#     serializer_class = HexagonSerializer
#     lookup_field = "id"  # change this to slug eventually?
#     filter_backends = (filters.DjangoFilterBackend, SearchFilter,)
#     filterset_class = MyHexFilter
#     search_fields = ['scores__species__english_name', 'scores__species__french_name', 'scores__week__week_number']


# alternative that only has score info

# class ScoreViewSet(ModelViewSet):
#     queryset = models.Score.objects.all()
#     serializer_class = ScoreSerializer
#     # lookup_field = "id"  # change this to slug eventually?
#     filter_backends = (filters.DjangoFilterBackend, SearchFilter,)
#     filterset_class = MyFilter
#     search_fields = ['species__english_name', 'species__french_name', 'week__week_number']
from ..models import Species, Week


class ScoreViewSet(ModelViewSet):
    queryset = models.Score.objects.all()
    serializer_class = ScoreSerializer

    def get_queryset(self):
        start = time.time()
        queryset = self.queryset.prefetch_related('week').prefetch_related('species')

        species_english_name = self.request.query_params.get('species')
        week_number = self.request.query_params.get('week')

        prefetch_filters = time.time()

        #custom filters by field
        if species_english_name is not None:
            # species = get_object_or_404(Species, english_name=species_english_name)
            queryset = queryset.filter(species__english_name=species_english_name)
        if week_number is not None:
            # week = get_object_or_404(Week, week_week_number=week_number)
            queryset = queryset.filter(week__week_number=week_number)

        end = time.time()


        print('start', prefetch_filters - start)
        print('prefetch_filter', end - prefetch_filters)
        print('total', end - start)

        return queryset


class ScoreFeatureViewSet(ModelViewSet):
    queryset = models.Score.objects.all()
    serializer_class = ScoreFeatureSerializer
    # pagination_class = pagination.StandardResultsSetPagination

    def get_queryset(self):
        start = time.time()
        queryset = self.queryset.prefetch_related('week').prefetch_related('species')

        species = self.request.query_params.get('species')
        week = self.request.query_params.get('week')
        site_score = self.request.query_params.get('site_score')

        prefetch_filters = time.time()


        #custom filters by field
        if species is not None:
            queryset = queryset.filter(species__english_name=species)
        if week is not None:
            queryset = queryset.filter(week__week_number=week)
        if site_score is not None:
            queryset = queryset.filter(site_score=site_score)

        end = time.time()

        print('start', prefetch_filters - start)
        print('prefetch_filter', end - prefetch_filters)
        print('total', end - start)

        return queryset

        # # get filter request from client:
        # filter_string = self.request.query_params.get('filter')

        # # apply filters if they are passed in using json format
        # # i.e. ?filter={"week__week_number":16}:
        # if filter_string is not None:
        #     filter_dictionary = json.loads(filter_string)
        #     queryset = queryset.filter(**filter_dictionary)




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

# LOOKUPS
##########

class SpeciesListAPIView(ListAPIView):
    queryset = models.Species.objects.all()
    serializer_class = SpeciesSerializer


class WeekListAPIView(ListAPIView):
    queryset = models.Week.objects.all()
    serializer_class = WeekSerializer
