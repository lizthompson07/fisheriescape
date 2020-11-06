from django.contrib.auth.models import User
from rest_framework import serializers

from projects2.models import ProjectYear


class UserDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username"]


class ProjectYearSerializer(serializers.ModelSerializer):
    def get_display_name(self, instance):
        return str(instance.fiscal_year)

    class Meta:
        model = ProjectYear
        exclude = ["updated_at", ]

    display_name = serializers.SerializerMethodField()
