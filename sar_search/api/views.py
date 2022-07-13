from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from . import serializers
from .. import models


# USER
############################
class SarSeachCurrentUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = serializers.UserDisplaySerializer(instance=request.user)
        data = serializer.data
        return Response(data)


# Records api view
############################
class SarSearchAPIView(APIView):
    permission_classes = []
    model = None
    model_instances = None

    def get(self, request):
        self.model_instances = self.model.objects.all()
        if request.query_params.get("pk"):
            pk = request.query_params.get("pk")
            self.model_instances = self.model_instances.filter(pk=pk).distinct()


# Points
############################
class PointsAPIView(SarSearchAPIView):
    model = models.Record

    def get(self, request):
        super().get(request)
        self.model_instances = self.model_instances.filter(record_type=1)
        if request.query_params.get("count"):
            data = {"record count": self.model_instances.count()}
            return Response(data)

        if request.query_params.get("limit"):
            record_num = int(request.query_params.get("limit"))
            if record_num < 0:
                self.model_instances = None
            else:
                self.model_instances = self.model_instances[:record_num]
        serializer = serializers.RecordDisplaySerializer(instance=self.model_instances, many=True)
        data = serializer.data
        return Response(data)


# Polygons
############################
class PolygonsAPIView(SarSearchAPIView):
    model = models.Record

    def get(self, request):
        super().get(request)
        self.model_instances = self.model_instances.filter(record_type__in=[2, 3])
        if request.query_params.get("limit"):
            record_num = int(request.query_params.get("limit"))
            if record_num < 0:
                self.model_instances = None
            else:
                self.model_instances = self.model_instances[:record_num]
        serializer = serializers.RecordDisplaySerializer(instance=self.model_instances, many=True)
        data = serializer.data
        return Response(data)


# Species
############################
class SpeciesAPIView(SarSearchAPIView):
    model = models.Species

    def get(self, request):
        super().get(request)
        if request.query_params.get("limit"):
            record_num = int(request.query_params.get("limit"))
            if record_num < 0:
                self.model_instances = None
            else:
                self.model_instances = self.model_instances[:record_num]
        serializer = serializers.SpeciesDisplaySerializer(instance=self.model_instances, many=True)
        data = serializer.data
        return Response(data)
