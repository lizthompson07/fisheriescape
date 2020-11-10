from django.contrib.auth.models import User
from rest_framework import serializers

from .. import models
from ..utils import can_modify_project


class UserDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username"]


class ProjectYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProjectYear
        exclude = ["updated_at", ]

    display_name = serializers.SerializerMethodField()

    def get_display_name(self, instance):
        return str(instance.fiscal_year)

    dates = serializers.SerializerMethodField()

    def get_dates(self, instance):
        return instance.dates

    metadata = serializers.SerializerMethodField()

    def get_metadata(self, instance):
        return instance.metadata

    deliverables_html = serializers.SerializerMethodField()

    def get_deliverables_html(self, instance):
        return instance.deliverables_html

    priorities_html = serializers.SerializerMethodField()

    def get_priorities_html(self, instance):
        return instance.priorities_html

    can_modify = serializers.SerializerMethodField()
    def get_can_modify(self, instance):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
            return can_modify_project(user, instance.project_id)

class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Staff
        fields = "__all__"

    # employee_type = serializers.StringRelatedField()
    # level = serializers.StringRelatedField()
    # funding_source = serializers.StringRelatedField()

    smart_name = serializers.SerializerMethodField()
    def get_smart_name(self, instance):
        return instance.smart_name