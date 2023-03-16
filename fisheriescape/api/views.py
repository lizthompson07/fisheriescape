from hashlib import md5

from django.core.checks import caches
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from .serializers import ScoreFeatureSerializer, SpeciesSerializer, WeekSerializer, VulnerableSpeciesSerializer, \
    VulnerableSpeciesSpotsSerializer
from .. import models
from fisheriescape.views import FisheriescapeAccessRequired


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


# class ScoreViewSet(ModelViewSet):
#     queryset = models.Score.objects.all()
#     serializer_class = ScoreSerializer
#
#     def get_queryset(self):
#         queryset = self.queryset.prefetch_related('week').prefetch_related('species')
#
#         species_english_name = self.request.query_params.get('species')
#         week_number = self.request.query_params.get('week')
#
#         #custom filters by field
#         if species_english_name is not None:
#             queryset = queryset.filter(species__english_name=species_english_name)
#         if week_number is not None:
#             queryset = queryset.filter(week__week_number=week_number)
#
#         return queryset


class ScoreFeatureView(FisheriescapeAccessRequired, ListAPIView):
    queryset = models.Score.objects.all()
    serializer_class = ScoreFeatureSerializer

    # Cache the results
    def list(self, request, *args, **kwargs):
        cache = caches.caches['default']
        species = self.request.query_params.get('species')
        week = self.request.query_params.get('week')
        cache_key = f"ScoreFeatureViewSet:{species}_{week}".encode('utf-8')
        hashed_cache_key = md5(cache_key).hexdigest()
        cached_results = cache.get(hashed_cache_key)
        if cached_results:
            return Response(cached_results)
        else:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            cache.set(hashed_cache_key, serializer.data)
            return Response(serializer.data)

    def get_queryset(self):
        queryset = self.queryset.prefetch_related('week').prefetch_related('species').prefetch_related("hexagon")

        species = self.request.query_params.get('species')
        week = self.request.query_params.get('week')
        site_score = self.request.query_params.get('site_score')

        # custom filters by field
        if species is not None:
            queryset = queryset.filter(species__english_name=species)
        if week is not None:
            queryset = queryset.filter(week__week_number=week)
        if site_score is not None:
            queryset = queryset.filter(site_score=site_score)

        return queryset


class VulnerableSpeciesSpotsView(FisheriescapeAccessRequired, ListAPIView):
    queryset = models.VulnerableSpeciesSpot.objects.all()
    serializer_class = VulnerableSpeciesSpotsSerializer

    # Cache the results
    def list(self, request, *args, **kwargs):
        cache = caches.caches['default']
        vulnerable_species = self.request.query_params.get('vulnerable_species')
        week = self.request.query_params.get('week')
        cache_key = f"VulnerableSpeciesSpotsView:{vulnerable_species}_{week}".encode('utf-8')
        hashed_cache_key = md5(cache_key).hexdigest()
        cached_results = cache.get(hashed_cache_key)
        if cached_results:
            return Response(cached_results)
        else:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            cache.set(hashed_cache_key, serializer.data)
            return Response(serializer.data)

    def get_queryset(self):
        queryset = self.queryset.prefetch_related('week').prefetch_related('vulnerable_species')

        vulnerable_species = self.request.query_params.get('vulnerable_species').split(',')
        week = self.request.query_params.get('week')

        # custom filters by field
        if vulnerable_species is not None:
            queryset = queryset.filter(vulnerable_species__english_name__in=vulnerable_species)
        if week is not None:
            queryset = queryset.filter(week__week_number=week)

        return queryset


# LOOKUPS
##########

class SpeciesListAPIView(ListAPIView):
    queryset = models.Species.objects.all()
    serializer_class = SpeciesSerializer


class VulnerableSpeciesView(FisheriescapeAccessRequired, ListAPIView):
    queryset = models.VulnerableSpecies.objects.all()
    serializer_class = VulnerableSpeciesSerializer


class WeekListAPIView(ListAPIView):
    queryset = models.Week.objects.all()
    serializer_class = WeekSerializer
