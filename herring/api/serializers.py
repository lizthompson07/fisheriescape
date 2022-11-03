from django.contrib.auth.models import User
from rest_framework import serializers

from .. import models
from ..utils import get_max_mins


class UserDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "username", ]


class LengthFrequencySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LengthFrequency
        fields = "__all__"


class SpeciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Species
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
    custom_message = serializers.SerializerMethodField()

    def get_flag_definition_display(self, instance):
        return instance.get_flag_definition_display()

    def get_custom_message(self, instance):

        if instance.flag_definition == 1:
            return f'The maximum probably length for this species is {instance.fish_detail.sample.species.max_length}mm'
        elif instance.flag_definition == 2:
            return f'The maximum probably weight for this species is {instance.fish_detail.sample.species.max_weight}g'
        elif instance.flag_definition == 3:
            return f'The maximum probably gonad weight for this species is {instance.fish_detail.sample.species.max_gonad_weight}g'
        elif instance.flag_definition == 4:
            return f'The maximum probably annulus count for this species is {instance.fish_detail.sample.species.max_annulus_count}'
        elif instance.flag_definition == 13:
            return f'The gonad sub-sample weight must be smaller than {instance.fish_detail.gonad_weight}g'
        elif instance.flag_definition > 4:
            max_min_lookup = get_max_mins(instance.fish_detail)
            if max_min_lookup.get(instance.flag_definition) and None not in [max_min_lookup.get(instance.flag_definition)["min"],
                                                                             max_min_lookup.get(instance.flag_definition)["max"]]:

                field_name = "fish weight"
                if instance.flag_definition == 11:
                    field_name = "gonad weight"
                elif instance.flag_definition == 12:
                    field_name = "annulus count"

                return f'We were expecting a {field_name} between {round(max_min_lookup[instance.flag_definition]["min"], 2)} and {round(max_min_lookup[instance.flag_definition]["max"], 2)}'


class FishDetailSerializer(serializers.ModelSerializer):
    flags = FishDetailFlagSerializer(many=True, read_only=True)
    species = serializers.SerializerMethodField()
    lab_sampler = serializers.StringRelatedField()
    otolith_sampler = serializers.StringRelatedField()

    def get_species(self, instance):
        return SpeciesSerializer(instance.sample.species).data

    class Meta:
        model = models.FishDetail
        fields = "__all__"
