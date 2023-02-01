from django.contrib.auth.models import User
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.db.models import Count, Avg, Sum
from django.utils.translation import gettext as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from lib.functions.custom_functions import listrify
from .. import models, utils
from ..utils import get_timezone_time


class UserDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "username", ]


class SampleSerializer(serializers.ModelSerializer):
    display = serializers.SerializerMethodField()
    datetime_display = serializers.SerializerMethodField()
    collection_display = serializers.SerializerMethodField()
    is_deletable = serializers.SerializerMethodField()
    sample_type_display = serializers.SerializerMethodField()
    coordinates = serializers.SerializerMethodField()
    collection_time_display = serializers.SerializerMethodField()

    def get_collection_time_display(self, instance):
        if instance.datetime:
            dt = get_timezone_time(instance.datetime)
            return f'{dt.strftime("%Y-%m-%d %H:%M")}<br>({naturaltime(instance.datetime)})'

    def get_coordinates(self, instance):
        return instance.coordinates

    def get_sample_type_display(self, instance):
        if instance.sample_type:
            return str(instance.sample_type)

    def get_is_deletable(self, instance):
        return instance.is_deletable

    def get_collection_display(self, instance):
        return str(instance.collection)

    def get_datetime_display(self, instance):
        if instance.datetime:
            dt = get_timezone_time(instance.datetime)
            return dt.strftime("%Y-%m-%d %H:%M")

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
    sample_obj = serializers.SerializerMethodField()
    has_extracts = serializers.SerializerMethodField()
    filtration_type_display = serializers.SerializerMethodField()
    info_display = serializers.SerializerMethodField()

    def get_info_display(self, instance):
        payload = list()
        if instance.is_filtration_blank:
            payload.append("filtration blank")
        if instance.sample and instance.sample.is_field_blank:
            payload.append("field blank")
        return listrify(payload)

    def get_filtration_type_display(self, instance):
        if instance.filtration_type:
            return str(instance.filtration_type)

    def get_sample_obj(self, instance):
        if instance.sample:
            return SampleSerializer(instance.sample).data

    def get_collection_display(self, instance):
        if instance.collection:
            return str(instance.collection)

    def get_batch_display(self, instance):
        return instance.filtration_batch.datetime.strftime("%Y-%m-%d")

    def get_start_datetime_display(self, instance):
        if instance.start_datetime:
            dt = get_timezone_time(instance.start_datetime)
            return dt.strftime("%Y-%m-%d %H:%M")

    def get_end_datetime_display(self, instance):
        if instance.end_datetime:
            dt = get_timezone_time(instance.end_datetime)
            return dt.strftime("%Y-%m-%d %H:%M")

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


class FilterSerializerLITE(serializers.ModelSerializer):
    class Meta:
        model = models.Filter
        fields = "__all__"

    filtration_type_display = serializers.SerializerMethodField()
    start_datetime_display = serializers.SerializerMethodField()
    end_datetime_display = serializers.SerializerMethodField()

    def get_filtration_type_display(self, instance):
        if instance.filtration_type:
            return str(instance.filtration_type)

    def get_start_datetime_display(self, instance):
        if instance.start_datetime:
            dt = get_timezone_time(instance.start_datetime)
            return dt.strftime("%Y-%m-%d %H:%M")

    def get_end_datetime_display(self, instance):
        if instance.end_datetime:
            dt = get_timezone_time(instance.end_datetime)
            return dt.strftime("%Y-%m-%d %H:%M")


class DNAExtractSerializer(serializers.ModelSerializer):
    display = serializers.SerializerMethodField()
    datetime_display = serializers.SerializerMethodField()
    batch_display = serializers.SerializerMethodField()
    filter_display = serializers.SerializerMethodField()
    sample_display = serializers.SerializerMethodField()
    filter_obj = serializers.SerializerMethodField()
    sample_obj = serializers.SerializerMethodField()
    has_pcrs = serializers.SerializerMethodField()
    dna_extraction_protocol_display = serializers.SerializerMethodField()
    info_display = serializers.SerializerMethodField()

    def get_info_display(self, instance):
        payload = list()
        if instance.is_extraction_blank:
            payload.append("extraction blank")
        if instance.filter and instance.filter.is_filtration_blank:
            payload.append("filtration blank")
        if instance.sample and instance.sample.is_field_blank:
            payload.append("field blank")
        return listrify(payload)

    def get_dna_extraction_protocol_display(self, instance):
        if instance.dna_extraction_protocol:
            return str(instance.dna_extraction_protocol)

    def get_has_pcrs(self, instance):
        return instance.pcrs.exists()

    def get_sample_obj(self, instance):
        if instance.sample:
            return SampleSerializer(instance.sample).data

    def get_filter_obj(self, instance):
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
            dt = get_timezone_time(instance.start_datetime)
            return dt.strftime("%Y-%m-%d %H:%M")

    def get_display(self, instance):
        return str(instance)

    class Meta:
        model = models.DNAExtract
        fields = "__all__"


class DNAExtractSerializerLITE(serializers.ModelSerializer):
    datetime_display = serializers.SerializerMethodField()
    dna_extraction_protocol_display = serializers.SerializerMethodField()
    collection_display = serializers.SerializerMethodField()

    def get_dna_extraction_protocol_display(self, instance):
        if instance.dna_extraction_protocol:
            return str(instance.dna_extraction_protocol)

    def get_datetime_display(self, instance):
        if instance.start_datetime:
            dt = get_timezone_time(instance.start_datetime)
            return dt.strftime("%Y-%m-%d %H:%M")

    def get_collection_display(self, instance):
        if instance.collection:
            return instance.collection.__str__()

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
    extract_obj = serializers.SerializerMethodField()
    batch_object = serializers.SerializerMethodField()
    pcr_assays = serializers.SerializerMethodField()

    def get_pcr_assays(self, instance):
        return PCRAssaySerializerLITE(instance.assays.all(), many=True).data

    def get_batch_object(self, instance):
        return PCRBatchSerializer(instance.pcr_batch).data

    def get_extract_obj(self, instance):
        if instance.extract:
            return DNAExtractSerializerLITE(instance.extract).data

    def get_assay_count(self, instance):
        return instance.assay_count

    def get_display(self, instance):
        return str(instance)


class PCRSerializerLITE(serializers.ModelSerializer):
    class Meta:
        model = models.PCR
        fields = "__all__"


class PCRResultsSerializer(serializers.Serializer):
    pcr_batch = serializers.IntegerField()
    extract = serializers.IntegerField()
    assay = serializers.SerializerMethodField()

    replicate_results = serializers.SerializerMethodField()

    def get_assay(self, instance):
        return instance["assay_pk"]

    def get_replicate_results(self, instance):
        pcr_assay_qs = self.context.get("pcr_assay_qs")
        result_qs = pcr_assay_qs.filter(assay=instance["assay_pk"],
                                        pcr__pcr_batch=instance["pcr_batch"],
                                        pcr__extract=instance["extract"]).values("ct", "edna_conc")
        return result_qs

    def to_representation(self, instance):
        data = super().to_representation(instance)

        pcr_assay_qs = self.context.get("pcr_assay_qs")
        result_qs = pcr_assay_qs.filter(assay=instance["assay_pk"],
                                        pcr__pcr_batch=instance["pcr_batch"],
                                        pcr__extract=instance["extract"])
        data["replicate_results"] = result_qs.values("ct", "edna_conc")
        if result_qs.aggregate(Sum("edna_conc"))["edna_conc__sum"]:
            data["mean_conc"] = result_qs.aggregate(Sum("edna_conc"))["edna_conc__sum"] / result_qs.count()
        else:
            data["mean_conc"] = 0
        data["threshold"] = result_qs.first().threshold
        lod = result_qs.first().assay.lod
        data["LOD"] = lod
        # get result:
        data["result"], data["result_display"] = utils.get_pcr_result(result_qs, lod)
        return data


class PCRAssaySerializer(serializers.ModelSerializer):
    pcr_obj = serializers.SerializerMethodField()
    result_display = serializers.SerializerMethodField()
    assay_display = serializers.SerializerMethodField()
    extraction_number = serializers.SerializerMethodField()
    info_display = serializers.SerializerMethodField()

    def get_info_display(self, instance):
        payload = list()
        if instance.pcr.extract:
            extract = instance.pcr.extract
            if extract.is_extraction_blank:
                payload.append("extraction blank")
            if extract.filter and extract.filter.is_filtration_blank:
                payload.append("filtration blank")
            if extract.sample and extract.sample.is_field_blank:
                payload.append("field blank")
        return listrify(payload)

    def get_extraction_number(self, instance):
        if instance.pcr.extract:
            return str(instance.pcr.extract.extraction_number)

    def get_assay_display(self, instance):
        if instance.assay:
            return str(instance.assay)

    def get_result_display(self, instance):
        return instance.get_result_display()

    def get_pcr_obj(self, instance):
        try:
            if instance.pcr:
                return PCRSerializer(instance.pcr).data
        except:
            pass

    class Meta:
        model = models.PCRAssay
        fields = "__all__"


class PCRAssaySerializerLITE(serializers.ModelSerializer):
    result_display = serializers.SerializerMethodField()
    assay_display = serializers.SerializerMethodField()
    lod = serializers.SerializerMethodField()

    def get_assay_display(self, instance):
        if instance.assay:
            return str(instance.assay)

    def get_lod(self, instance):
        if instance.assay:
            return instance.assay.lod

    def get_result_display(self, instance):
        return instance.get_result_display()

    class Meta:
        model = models.PCRAssay
        fields = "__all__"


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Collection
        fields = "__all__"

    date_display = serializers.SerializerMethodField()

    def get_date_display(self, instance):
        if instance.start_date:
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


class PCRBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PCRBatch
        fields = "__all__"


class AssaySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Assay
        fields = "__all__"

    species_display = serializers.SerializerMethodField()
    master_mix_display = serializers.SerializerMethodField()
    max_replicates = serializers.SerializerMethodField()

    def get_species_display(self, instance):
        return instance.species_display

    def get_master_mix_display(self, instance):
        if instance.master_mix:
            return instance.master_mix.__str__()

    def get_max_replicates(self, instance):
        collection_id = self.context.get("collection_id")
        if collection_id:
            pcr_assay_qs = models.PCRAssay.objects.filter(pcr__collection=collection_id, assay=instance)
            pcr_max_rep_count = pcr_assay_qs.values("pcr__extract", "pcr__pcr_batch").annotate(count=Count('id')).order_by("-count").first()['count']
            return pcr_max_rep_count
        return 0
