from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

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
    start_datetime_display = serializers.SerializerMethodField()
    end_datetime_display = serializers.SerializerMethodField()
    batch_display = serializers.SerializerMethodField()
    collection_display = serializers.SerializerMethodField()
    sample_object = serializers.SerializerMethodField()
    has_extracts = serializers.SerializerMethodField()

    def get_sample_object(self, instance):
        if instance.sample:
            return SampleSerializer(instance.sample).data

    def get_collection_display(self, instance):
        if instance.collection:
            return str(instance.collection)

    def get_batch_display(self, instance):
        return instance.filtration_batch.datetime.strftime("%Y-%m-%d")

    def get_start_datetime_display(self, instance):
        if instance.start_datetime:
            return instance.start_datetime.strftime("%Y-%m-%d %H:%M")

    def get_end_datetime_display(self, instance):
        if instance.end_datetime:
            return instance.end_datetime.strftime("%Y-%m-%d %H:%M")

    def get_display(self, instance):
        return str(instance)

    def get_has_extracts(self, instance):
        return instance.extracts.exists()

    class Meta:
        model = models.Filter
        fields = "__all__"

    def validate(self, attrs):
        """
        form validation:
        - make that there is at least a project, project year or status report
        """
        start_datetime = attrs.get("start_datetime")
        end_datetime = attrs.get("end_datetime")

        if start_datetime and end_datetime and start_datetime > end_datetime:
            msg = _('The end date must occur after the start date.')
            raise ValidationError(msg)
        return attrs


class DNAExtractSerializer(serializers.ModelSerializer):
    display = serializers.SerializerMethodField()
    datetime_display = serializers.SerializerMethodField()
    batch_display = serializers.SerializerMethodField()
    filter_display = serializers.SerializerMethodField()
    sample_display = serializers.SerializerMethodField()
    filter_object = serializers.SerializerMethodField()
    sample_object = serializers.SerializerMethodField()
    has_pcrs = serializers.SerializerMethodField()

    def get_has_pcrs(self, instance):
        return instance.pcrs.exists()

    def get_sample_object(self, instance):
        if instance.sample:
            return SampleSerializer(instance.sample).data

    def get_filter_object(self, instance):
        if instance.filter:
            return FilterSerializer(instance.filter).data

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

    extract_object = serializers.SerializerMethodField()

    def get_extract_object(self, instance):
        if instance.extract:
            return DNAExtractSerializer(instance.extract).data

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


class SampleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SampleType
        fields = "__all__"
