
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from shapely.errors import WKTReadingError
from shapely.geometry import Point, Polygon
from shapely import wkt

from . import serializers
from .. import models


# USER
#######
class CurrentPublicationUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = serializers.UserDisplaySerializer(instance=request.user)
        data = serializer.data
        return Response(data)


# Pubs
#######
class PublicationsAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    # sample WKT polygon:
    # POLYGON((45 -60, 46 -60, 46 -61, 45 -61, 45 -60))

    def get(self, request):
        lat = lon = sar = start_year = end_year = wkt_poly = False
        if request.query_params.get("lat"):
            lat = float(request.query_params.get("lat"))
        if request.query_params.get("lon"):
            lon = float(request.query_params.get("lon"))
        if request.query_params.get("sar"):
            sar = request.query_params.get("sar")
        if request.query_params.get("start_year"):
            start_year = request.query_params.get("start_year")
        if request.query_params.get("end_year"):
            end_year = request.query_params.get("end_year")
        if request.query_params.get("wkt_poly"):
            wkt_poly = request.query_params.get("wkt_poly")

        geoscope_instaces = models.GeographicScope.objects.all()
        proj_instances = models.Project.objects.none()
        poly_qs = [models.Polygon.objects.filter(geoscope=gs.pk) for gs in geoscope_instaces]
        poly_dict = {}
        for poly in poly_qs:
            if len(poly) > 2:
                pt_list = [(pt.latitude, pt.longitude) for pt in poly]
                poly_dict[str(poly[0].geoscope.pk)] = Polygon(pt_list)

        if lat and lon:
            pt = Point(lat, lon)
            proj_instances = models.Project.objects.none()
            for geoscope, polygon in poly_dict.items():
                if polygon.contains(pt):
                    proj_instances = proj_instances | models.Project.objects.filter(geographic_scope=int(geoscope))
        elif wkt_poly:
            try:
                query_poly = wkt.loads(wkt_poly)
            except WKTReadingError:
                data = [{"error": "Invalid WKT formating. Unable to parse wkt_poly argument with shapely.wkt.loads()"}]
                return Response(data)
            proj_instances = models.Project.objects.none()
            for geoscope, polygon in poly_dict.items():
                if polygon.intersects(query_poly):
                    proj_instances = proj_instances | models.Project.objects.filter(geographic_scope=int(geoscope))

        if sar:
            proj_instances = proj_instances.filter(theme__name__iexact="SPECIES AT RISK")

        if start_year:
            proj_instances = proj_instances.filter(year__gte=start_year)

        if end_year:
            proj_instances = proj_instances.filter(year__lte=end_year)

        proj_instances = proj_instances.filter().distinct()

        serializer = serializers.PubsDisplaySerializer(instance=proj_instances, many=True,  context={'request': request})
        data = serializer.data
        return Response(data)
