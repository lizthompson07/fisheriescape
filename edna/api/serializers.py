from django.contrib.auth.models import User
from rest_framework import serializers

from .. import models


class UserDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "username", ]


class SampleSerializer(serializers.ModelSerializer):
    display = serializers.SerializerMethodField()
    datetime_display = serializers.SerializerMethodField()
    collection_display = serializers.SerializerMethodField()

    def get_collection_display(self, instance):
        return str(instance.collection)

    def get_datetime_display(self, instance):
        if instance.datetime:
            return instance.datetime.strftime("%Y-%m-%d %H:%M")

    def get_display(self, instance):
        return str(instance)

    class Meta:
        model = models.Sample
        fields = "__all__"


class FilterSerializer(serializers.ModelSerializer):
    display = serializers.SerializerMethodField()
    datetime_display = serializers.SerializerMethodField()
    batch_display = serializers.SerializerMethodField()

    def get_batch_display(self, instance):
        return instance.filtration_batch.datetime.strftime("%Y-%m-%d")

    def get_datetime_display(self, instance):
        if instance.start_datetime:
            return instance.start_datetime.strftime("%Y-%m-%d %H:%M")

    def get_display(self, instance):
        return str(instance)

    class Meta:
        model = models.Filter
        fields = "__all__"


class DNAExtractSerializer(serializers.ModelSerializer):
    display = serializers.SerializerMethodField()
    datetime_display = serializers.SerializerMethodField()
    batch_display = serializers.SerializerMethodField()

    filter_display = serializers.SerializerMethodField()

    sample_display = serializers.SerializerMethodField()

    def get_sample_display(self, instance):
        if instance.filter and instance.filter.sample:
            return instance.filter.sample.display

    def get_filter_display(self, instance):
        if instance.filter:
            return instance.filter.display

    def get_batch_display(self, instance):
        return instance.extraction_batch.datetime.strftime("%Y-%m-%d")

    def get_datetime_display(self, instance):
        if instance.start_datetime:
            return instance.start_datetime.strftime("%Y-%m-%d %H:%M")

    def get_display(self, instance):
        return str(instance)

    class Meta:
        model = models.DNAExtract
        fields = "__all__"


# class SpeciesObservationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = models.SpeciesObservation
#         fields = "__all__"
#
#     species_display = serializers.SerializerMethodField()
#
#     def get_species_display(self, instance):
#         return str(instance.species)


class PCRSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PCR
        fields = "__all__"

    display = serializers.SerializerMethodField()
    assay_count = serializers.SerializerMethodField()

    def get_assay_count(self, instance):
        return instance.assay_count

    def get_display(self, instance):
        return str(instance)


class PCRAssaySerializer(serializers.ModelSerializer):
    pcr_object = serializers.SerializerMethodField()
    result_display = serializers.SerializerMethodField()

    def get_result_display(self, instance):
        return instance.get_result_display()

    def get_pcr_object(self, instance):
        return PCRSerializer(instance.pcr).data

    class Meta:
        model = models.PCRAssay
        fields = "__all__"

    # display = serializers.SerializerMethodField()
    #
    # def get_display(self, instance):
    #     return str(instance)


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Collection
        fields = "__all__"

    date_display = serializers.SerializerMethodField()

    def get_date_display(self, instance):
        return instance.start_date.strftime("%Y-%m-%d")


class ExtractionBatchSerializer(serializers.ModelSerializer):
    display = serializers.SerializerMethodField()

    def get_display(self, instance):
        return instance.datetime.strftime("%Y-%m-%d")

    class Meta:
        model = models.ExtractionBatch
        fields = "__all__"


class FiltrationBatchSerializer(serializers.ModelSerializer):
    display = serializers.SerializerMethodField()

    def get_display(self, instance):
        return instance.datetime.strftime("%Y-%m-%d")

    class Meta:
        model = models.FiltrationBatch
        fields = "__all__"
