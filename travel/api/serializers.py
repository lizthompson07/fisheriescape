from django.contrib.auth.models import User
from rest_framework import serializers

from .. import models


# from ..utils import can_modify_project


class UserDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username"]


class TripRequestCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TripRequestCost
        fields = "__all__"

    cost_display = serializers.SerializerMethodField()

    def get_cost_display(self, instance):
        return str(instance.cost)

#
# class ProjectYearSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = models.ProjectYear
#         exclude = ["updated_at", ]
#
#     display_name = serializers.SerializerMethodField()
#     dates = serializers.SerializerMethodField()
#     metadata = serializers.SerializerMethodField()
#     deliverables_html = serializers.SerializerMethodField()
#     priorities_html = serializers.SerializerMethodField()
#     can_modify = serializers.SerializerMethodField()
#
#     def get_display_name(self, instance):
#         return str(instance.fiscal_year)
#
#     def get_dates(self, instance):
#         return instance.dates
#
#     def get_metadata(self, instance):
#         return instance.metadata
#
#     def get_deliverables_html(self, instance):
#         return instance.deliverables_html
#
#     def get_priorities_html(self, instance):
#         return instance.priorities_html
#
#     def get_can_modify(self, instance):
#         user = None
#         request = self.context.get("request")
#         if request and hasattr(request, "user"):
#             user = request.user
#             return can_modify_project(user, instance.project_id)
#
#
# class StaffSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = models.Staff
#         exclude = ["project_year"]
#
#     # employee_type = serializers.StringRelatedField()
#     # level = serializers.StringRelatedField()
#     # funding_source = serializers.StringRelatedField()
#
#     smart_name = serializers.SerializerMethodField()
#     employee_type_display = serializers.SerializerMethodField()
#     level_display = serializers.SerializerMethodField()
#     funding_source_display = serializers.SerializerMethodField()
#
#     def get_smart_name(self, instance):
#         return instance.smart_name
#
#     def get_employee_type_display(self, instance):
#         return str(instance.employee_type)
#
#     def get_level_display(self, instance):
#         return str(instance.level)
#
#     def get_funding_source_display(self, instance):
#         return str(instance.funding_source)
