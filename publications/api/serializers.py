from django.contrib.auth.models import User
from rest_framework import serializers
from .. import models
from django.urls import reverse_lazy


class UserDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "username"]


class PubsDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Project
        fields = ["title", "year", "abstract", "method", "publications", "dmapps_url"]

    publications = serializers.SerializerMethodField()
    dmapps_url = serializers.SerializerMethodField()

    def get_publications(self, instance):
        pub_qs = models.Publication.objects.filter(project__id=instance.id)
        if pub_qs.count() == 1:
            return [pub_qs.get().__str__()]
        elif pub_qs.count() == 0:
            return None
        else:
            return [pub.get().__str__() for pub in pub_qs]

    def get_dmapps_url(self, instance):
        base_url = self.context['request'].META["HTTP_HOST"]
        return "{}{}".format(base_url, reverse_lazy("publications:prj_detail", kwargs={'pk': instance.id}))
