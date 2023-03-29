from collections import OrderedDict

from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.relations import StringRelatedField
from rest_framework.serializers import LIST_SERIALIZER_KWARGS, ListSerializer, ModelSerializer
from rest_framework_gis.serializers import GeoFeatureModelSerializer, GeometrySerializerMethodField
from django.db import models
from drf_extra_fields.geo_fields import PointField

from fisheriescape.models import Score, Hexagon, Species, Week, VulnerableSpecies, VulnerableSpeciesSpot


## doesn't work with leaflet implementation as yet

class ScoreSerializer(serializers.ModelSerializer):
    """A class to serialize score to pass into HexagonSerializer as nested"""

    species = StringRelatedField()
    week = StringRelatedField()
    grid_id = SerializerMethodField()

    def get_grid_id(self, obj):
        return obj.hexagon.grid_id

    class Meta:
        model = Score
        fields = "__all__"


class HexagonSerializer(GeoFeatureModelSerializer):
    """A class to serialize hex polygons with nested information from Score model through related field"""
    scores = ScoreSerializer(read_only=True, many=True)

    class Meta:
        model = Hexagon
        geo_field = 'polygon'
        fields = "__all__"


# Standalone without hexagon names

# ## NOTES: GeoFeatureModelSerializer did not work with Filter in view
#
# class ScoreSerializer(GeoModelSerializer):
#     """A class to serialize hex polygons as GeoJSON compatible data"""
#
#     hexagon = GeometrySerializerMethodField()
#     species = StringRelatedField()
#     week = StringRelatedField()
#
#     def get_hexagon(self, obj):
#         return obj.hexagon.polygon
#
#     class Meta:
#         model = Score
#         geo_field = 'hexagon'
#         fields = "__all__"
#
#
## BUT need GeoFeatureModelSerializer to use getJSON in map3.js---is there another way to import api endpoint into .js file?

class CustomGeoFeatureModelListSerializer(ListSerializer):
    @property
    def data(self):
        return super(ListSerializer, self).data

    def to_representation(self, data):
        """
        Add GeoJSON compatible formatting to a serialized queryset list
        """
        max_fs_score = 0
        if data:
            if isinstance(data[0], Score):
                # Single species
                species_list = {score.species for score in data.all()}
                max_fs_score = sum(
                    [Score.objects.filter(species=species).aggregate(models.Max('fs_score')).get('fs_score__max') for
                     species in species_list])
            else:
                # Combined data from multiple species
                species_names = set()
                for score in data:
                    species_names.update(score.get('species').split(','))

                for species in species_names:
                    species_max_fs_score = Score.objects.filter(species__english_name=species).aggregate(
                        models.Max('fs_score')).get('fs_score__max')
                    max_fs_score += species_max_fs_score

        return OrderedDict(
            (
                ("type", "FeatureCollection"),
                ("max_fs_score", max_fs_score),
                ("features", super().to_representation(data)),
            )
        )


class ScoreFeatureSerializer(GeoFeatureModelSerializer):
    """A class to serialize hex polygons as GeoJSON compatible data"""

    hexagon = GeometrySerializerMethodField()
    species = StringRelatedField()
    week = StringRelatedField()
    grid_id = SerializerMethodField()

    def get_hexagon(self, obj):
        return obj.hexagon.polygon

    def get_grid_id(self, obj):
        return obj.hexagon.grid_id

    class Meta:
        model = Score
        geo_field = 'hexagon'
        fields = "__all__"

    # Override base method to use our custom GeoFeatureModelListSerializer
    @classmethod
    def many_init(cls, *args, **kwargs):
        child_serializer = cls(*args, **kwargs)
        list_kwargs = {'child': child_serializer}
        list_kwargs.update(
            {
                key: value
                for key, value in kwargs.items()
                if key in LIST_SERIALIZER_KWARGS
            }
        )
        meta = getattr(cls, 'Meta', None)
        list_serializer_class = getattr(
            meta, 'list_serializer_class', CustomGeoFeatureModelListSerializer
        )
        return list_serializer_class(*args, **list_kwargs)


class ScoreFeatureCombinedSerializer(GeoFeatureModelSerializer):
    """A class to serialize hex polygons as GeoJSON compatible data"""

    hexagon = GeometrySerializerMethodField()
    species = StringRelatedField()
    week = StringRelatedField()
    grid_id = SerializerMethodField()
    species_count = SerializerMethodField()

    def get_hexagon(self, obj):
        hexagon_id = obj.get('hexagon')
        return Hexagon.objects.get(id=hexagon_id).polygon

    def get_grid_id(self, obj):
        hexagon_id = obj.get('hexagon')
        return Hexagon.objects.get(id=hexagon_id).grid_id

    def get_species_count(self, obj):
        return obj.get('species_count')

    class Meta:
        model = Score
        id_field = None
        geo_field = 'hexagon'
        fields = "__all__"

    # Override base method to use our custom GeoFeatureModelListSerializer
    @classmethod
    def many_init(cls, *args, **kwargs):
        child_serializer = cls(*args, **kwargs)
        list_kwargs = {'child': child_serializer}
        list_kwargs.update(
            {
                key: value
                for key, value in kwargs.items()
                if key in LIST_SERIALIZER_KWARGS
            }
        )
        meta = getattr(cls, 'Meta', None)
        list_serializer_class = getattr(
            meta, 'list_serializer_class', CustomGeoFeatureModelListSerializer
        )
        return list_serializer_class(*args, **list_kwargs)


class VulnerableSpeciesSpotsSerializer(ModelSerializer):
    point = PointField()
    vulnerable_species = StringRelatedField()
    week = StringRelatedField()

    class Meta:
        model = VulnerableSpeciesSpot
        # geo_field = "point"
        fields = "__all__"

    # # Override base method to use our custom GeoFeatureModelListSerializer
    # @classmethod
    # def many_init(cls, *args, **kwargs):
    #     child_serializer = cls(*args, **kwargs)
    #     list_kwargs = {'child': child_serializer}
    #     list_kwargs.update(
    #         {
    #             key: value
    #             for key, value in kwargs.items()
    #             if key in LIST_SERIALIZER_KWARGS
    #         }
    #     )
    #     meta = getattr(cls, 'Meta', None)
    #     list_serializer_class = getattr(
    #         meta, 'list_serializer_class', CustomGeoFeatureModelListSerializer
    #     )
    #     return list_serializer_class(*args, **list_kwargs)


# For testing
# class ScoreSerializer(serializers.ModelSerializer):
#     """A class to serialize hex polygons as GeoJSON compatible data"""
#
#     class Meta:
#         model = Species
#         fields = "__all__"

class SpeciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Species
        fields = "__all__"


class VulnerableSpeciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = VulnerableSpecies
        fields = "__all__"


class WeekSerializer(serializers.ModelSerializer):
    date_range_text = SerializerMethodField()

    def get_date_range_text(self, obj):
        try:
            string = "{} to {}".format(obj.approx_start.strftime("%d-%b"), obj.approx_end.strftime("%d-%b"))
            return string
        except AttributeError:
            return None

    class Meta:
        model = Week
        fields = "__all__"
