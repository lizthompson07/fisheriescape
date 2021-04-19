from django.contrib.auth.models import User
from rest_framework import serializers

from .. import models


class UserDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "username", ]


class SampleSpeciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SampleSpecies
        fields = "__all__"


class LineSpeciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LineSpecies
        fields = "__all__"


class SurfaceSpeciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SurfaceSpecies
        fields = "__all__"


class IncidentalReportSpeciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.IncidentalReportSpecies
        fields = "__all__"



class CrabSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Catch
        exclude = [
            "count",
        ]

class BycatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Catch
        exclude = [
            "width",
            "sex",
            "carapace_color",
            "abdomen_color",
            "egg_color",
        ]

