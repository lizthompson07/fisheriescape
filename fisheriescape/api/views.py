from django_filters import FilterSet
from rest_framework import generics
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework import viewsets
from rest_framework import mixins

from .serializers import ScoreSerializer
from .. import models


# class EntryCSVAPIView(ListAPIView):
#     renderer_classes = [CSVRenderer]
#     serializer_class = serializers.EntrySerializer
#     permission_classes = [permissions.IsAuthenticatedOrReadOnly]
#     queryset = models.Entry.objects.all()

class MyFilter(FilterSet):
    class Meta:
        model = models.Score
        fields = ['species', 'site_score']


## for nested relationship

# class ScoreViewSet(ReadOnlyModelViewSet):
#     queryset = models.Hexagon.objects.all()
#     serializer_class = HexagonSerializer


class ScoreViewSet(ModelViewSet):
    queryset = models.Score.objects.all()
    serializer_class = ScoreSerializer

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