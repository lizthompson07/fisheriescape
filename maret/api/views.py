
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet


from . import permissions
from . import serializers
from .. import models


class CommitteeViewSet(ModelViewSet):
    queryset = models.Committee.objects.all()
    serializer_class = serializers.ComitteeSerializer
    permission_classes = [permissions.CanReadOnly]

    def retrieve(self, request, *args, **kwargs):
        instance = get_object_or_404(models.Committee, pk=self.kwargs.get("pk"))
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
