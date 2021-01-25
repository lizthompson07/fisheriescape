from django.contrib.auth.models import User
from rest_framework import serializers

from .. import models


class UserDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "username", ]


class SectionLITESerializer(serializers.ModelSerializer):
    substrate_profile = serializers.SerializerMethodField()
    observation_count = serializers.SerializerMethodField()

    def get_observation_count(self, instance):
        return instance.observations.count()

    def get_substrate_profile(self, instance):
        return instance.substrate_profile

    class Meta:
        model = models.Section
        fields = "__all__"


class ObservationSerializer(serializers.ModelSerializer):
    section = SectionLITESerializer(read_only=True)
    sex_display = serializers.SerializerMethodField()
    egg_status_display = serializers.SerializerMethodField()
    certainty_rating_display = serializers.SerializerMethodField()

    def get_certainty_rating_display(self, instance):
        return instance.certainty_rating_special_display

    def get_egg_status_display(self, instance):
        return instance.egg_status_special_display

    def get_sex_display(self, instance):
        return instance.sex_special_display

    class Meta:
        model = models.Observation
        fields = "__all__"


class SectionSerializer(serializers.ModelSerializer):
    observations = ObservationSerializer(many=True, read_only=True)
    substrate_profile = serializers.SerializerMethodField()

    def get_substrate_profile(self, instance):
        return instance.substrate_profile

    class Meta:
        model = models.Section
        fields = "__all__"
