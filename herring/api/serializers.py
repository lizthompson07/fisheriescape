from django.contrib.auth.models import User
from rest_framework import serializers

from .. import models


class UserDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "username", ]


class LengthFrequencySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LengthFrequency
        fields = "__all__"


class SampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Sample
        fields = "__all__"


class FishDetailFlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FishDetailFlag
        fields = "__all__"

    flag_definition_display = serializers.SerializerMethodField()

    def get_flag_definition_display(self, instance):
        return instance.get_flag_definition_display()

class FishDetailSerializer(serializers.ModelSerializer):
    flags = FishDetailFlagSerializer(many=True, read_only=True)

    class Meta:
        model = models.FishDetail
        fields = "__all__"
