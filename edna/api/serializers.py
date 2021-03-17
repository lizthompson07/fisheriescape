from django.contrib.auth.models import User
from rest_framework import serializers
from .. import models

class UserDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "username", ]


class FilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Filter
        fields = "__all__"



class DNAExtractSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DNAExtract
        fields = "__all__"



class PCRSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PCR
        fields = "__all__"


