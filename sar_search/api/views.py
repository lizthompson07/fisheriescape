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
    """
    Returns a list of all records with a point geometry type, along with the geometry type.

    Parameters include:

       - count: returns total number of point geometry records. e.g. [dmapps/api/sar-search/points/?count=True](http://dmapps/api/sar-search/points/?count=True)

       - limit: limit the number of records returned to the value: e.g. [dmapps/api/sar-search/points/?limit=5](http://dmapps/api/sar-search/points/?limit=5)

    Other relevant API's:

    - Species: ([dmapps/api/sar-search/species/](http://dmapps/api/sar-search/species/)) Provides information on each species record, id field links to the
     species field in the points API.

    - Polygons: ([dmapps/api/sar-search/polygons/](http://dmapps/api/sar-search/polygons/?limit=5)) Similar to the points API, but for line and polygon geometry records.

    """
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
    """
       Returns a list of all records with polygon or line geometry type, along with the geometry type.

       Parameters include:

       - count: returns total number of polygon and line geometry records. e.g. [dmapps/api/sar-search/polygons/?count=True](http://dmapps/api/sar-search/polygons/?count=True)

       - limit: limit the number of records returned to the value: e.g. [dmapps/api/sar-search/polygons/?limit=5](http://dmapps/api/sar-search/polygons/?limit=5)

       Other relevant API's:

       - Species: ([dmapps/api/sar-search/species/](http://dmapps/api/sar-search/species/)) Provides information on each species record, id field links to the
        species field in the polygons API.

      - Points: ([dmapps/api/sar-search/points/](http://dmapps/api/sar-search/points/?limit=5)) Similar to the polygons API, but for point geometry records.

       """
    model = models.Record

    def get(self, request):
        super().get(request)
        self.model_instances = self.model_instances.filter(record_type__in=[2, 3])

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


# Species
############################
class SpeciesAPIView(SarSearchAPIView):
    """
   Returns a list of all speices details.

   Parameters include:

      - count: returns total number of species records. e.g. [dmapps/api/sar-search/species/?count=True](http://dmapps/api/sar-search/species/?count=True)

      - limit: limit the number of records returned to the value: e.g. [dmapps/api/sar-search/species/?limit=5](http://dmapps/api/sar-search/species/?limit=5)

   Other relevant API's:

    - Points: ([dmapps/api/sar-search/points/](http://dmapps/api/sar-search/points/?limit=5)) Returns point geometry records present in SAR search.

   - Polygons: ([dmapps/api/sar-search/polygons/](http://dmapps/api/sar-search/polygons/?limit=5)) Returns line and polygon geometry records present in SAR search.

   """
    model = models.Species

    def get(self, request):
        super().get(request)

        if request.query_params.get("count"):
            data = {"record count": self.model_instances.count()}
            return Response(data)

        if request.query_params.get("limit"):
            record_num = int(request.query_params.get("limit"))
            if record_num < 0:
                self.model_instances = None
            else:
                self.model_instances = self.model_instances[:record_num]
        serializer = serializers.SpeciesDisplaySerializer(instance=self.model_instances, many=True)
        data = serializer.data
        return Response(data)
