from rest_framework import serializers
from rest_framework.relations import StringRelatedField
from rest_framework_gis.serializers import GeoFeatureModelSerializer, GeometrySerializerMethodField, GeoModelSerializer

from fisheriescape.models import Score, Hexagon, Species


## doesn't work with leaflet implementation as yet

# class ScoreSerializer(serializers.ModelSerializer):
#     """A class to serialize score to pass into HexagonSerializer as nested"""
#
#     species = StringRelatedField()
#     week = StringRelatedField()
#
#     class Meta:
#         model = Score
#         fields = "__all__"
#
#
# class HexagonSerializer(GeoFeatureModelSerializer):
#     """A class to serialize hex polygons with nested information from Score model through related field"""
#     scores = ScoreSerializer(read_only=True, many=True)
#
#     class Meta:
#         model = Hexagon
#         geo_field = 'polygon'
#         fields = "__all__"

# Standalone without hexagon names

## NOTES: GeoFeatureModelSerializer did not work with Filter in view

class ScoreSerializer(GeoModelSerializer):
    """A class to serialize hex polygons as GeoJSON compatible data"""

    hexagon = GeometrySerializerMethodField()
    species = StringRelatedField()
    week = StringRelatedField()

    def get_hexagon(self, obj):
        return obj.hexagon.polygon

    class Meta:
        model = Score
        geo_field = 'hexagon'
        fields = "__all__"


## BUT need GeoFeatureModelSerializer to use getJSON in map3.js---is there another way to import api endpoint into .js file?
class ScoreFeatureSerializer(GeoFeatureModelSerializer):
    """A class to serialize hex polygons as GeoJSON compatible data"""

    hexagon = GeometrySerializerMethodField()
    species = StringRelatedField()
    week = StringRelatedField()

    def get_hexagon(self, obj):
        return obj.hexagon.polygon

    class Meta:
        model = Score
        geo_field = 'hexagon'
        fields = "__all__"


# For testing
# class ScoreSerializer(serializers.ModelSerializer):
#     """A class to serialize hex polygons as GeoJSON compatible data"""
#
#     class Meta:
#         model = Species
#         fields = "__all__"