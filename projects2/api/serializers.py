from django.contrib.auth.models import User
from markdown import markdown
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
    dates = serializers.SerializerMethodField()
    metadata = serializers.SerializerMethodField()
    can_modify = serializers.SerializerMethodField()
    submitted = serializers.SerializerMethodField()

    deliverables_html = serializers.SerializerMethodField()
    priorities_html = serializers.SerializerMethodField()
    technical_service_needs_html = serializers.SerializerMethodField()
    mobilization_needs_html = serializers.SerializerMethodField()
    vehicle_needs_html = serializers.SerializerMethodField()
    ship_needs_html = serializers.SerializerMethodField()
    field_staff_needs_html = serializers.SerializerMethodField()
    instrumentation_html = serializers.SerializerMethodField()
    data_collected_html = serializers.SerializerMethodField()
    data_products_html = serializers.SerializerMethodField()
    data_storage_plan_html = serializers.SerializerMethodField()
    data_management_needs_html = serializers.SerializerMethodField()
    other_lab_support_needs_html = serializers.SerializerMethodField()
    it_needs_html = serializers.SerializerMethodField()
    default_funding_source_id = serializers.SerializerMethodField()

    def get_display_name(self, instance):
        return str(instance.fiscal_year)

    def get_dates(self, instance):
        return instance.dates

    def get_metadata(self, instance):
        return instance.metadata

    def get_deliverables_html(self, instance):
        return instance.deliverables_html

    def get_priorities_html(self, instance):
        return instance.priorities_html

    def get_technical_service_needs_html(self, instance):
        return markdown(instance.technical_service_needs) if instance.technical_service_needs else None

    def get_mobilization_needs_html(self, instance):
        return markdown(instance.mobilization_needs) if instance.mobilization_needs else None

    def get_vehicle_needs_html(self, instance):
        return markdown(instance.vehicle_needs) if instance.vehicle_needs else None

    def get_ship_needs_html(self, instance):
        return markdown(instance.ship_needs) if instance.ship_needs else None

    def get_instrumentation_html(self, instance):
        return markdown(instance.instrumentation) if instance.instrumentation else None

    def get_data_collected_html(self, instance):
        return markdown(instance.data_collected) if instance.data_collected else None

    def get_data_products_html(self, instance):
        return markdown(instance.data_products) if instance.data_products else None

    def get_data_storage_plan_html(self, instance):
        return markdown(instance.data_storage_plan) if instance.data_storage_plan else None

    def get_data_management_needs_html(self, instance):
        return markdown(instance.data_management_needs) if instance.data_management_needs else None

    def get_other_lab_support_needs_html(self, instance):
        return markdown(instance.other_lab_support_needs) if instance.other_lab_support_needs else None

    def get_it_needs_html(self, instance):
        return markdown(instance.it_needs) if instance.it_needs else None

    def get_field_staff_needs_html(self, instance):
        return markdown(instance.field_staff_needs) if instance.field_staff_needs else None

    def get_can_modify(self, instance):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
            return can_modify_project(user, instance.project_id)

    def get_submitted(self, instance):
        if instance.submitted:
            return instance.submitted.strftime("%Y-%m-%d")

    def get_default_funding_source_id(self, instance):
        return instance.project.default_funding_source_id


class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Staff
        exclude = ["project_year"]

    # employee_type = serializers.StringRelatedField()
    # level = serializers.StringRelatedField()
    # funding_source = serializers.StringRelatedField()

    smart_name = serializers.SerializerMethodField()
    employee_type_display = serializers.SerializerMethodField()
    level_display = serializers.SerializerMethodField()
    funding_source_display = serializers.SerializerMethodField()
    student_program_display = serializers.SerializerMethodField()
    project_year_id = serializers.SerializerMethodField()

    def get_smart_name(self, instance):
        return instance.smart_name

    def get_employee_type_display(self, instance):
        return str(instance.employee_type)

    def get_level_display(self, instance):
        return str(instance.level)

    def get_funding_source_display(self, instance):
        return str(instance.funding_source)

    def get_student_program_display(self, instance):
        return instance.get_student_program_display()

    def get_project_year_id(self, instance):
        return instance.project_year_id


class OMCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OMCost
        exclude = ["project_year"]

    funding_source_display = serializers.SerializerMethodField()
    om_category_display = serializers.SerializerMethodField()
    project_year_id = serializers.SerializerMethodField()
    category_type = serializers.SerializerMethodField()

    def get_funding_source_display(self, instance):
        return str(instance.funding_source)

    def get_om_category_display(self, instance):
        return str(instance.om_category)

    def get_project_year_id(self, instance):
        return instance.project_year_id

    def get_category_type(self, instance):
        return instance.category_type


class CapitalCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CapitalCost
        exclude = ["project_year"]

    funding_source_display = serializers.SerializerMethodField()
    category_display = serializers.SerializerMethodField()
    project_year_id = serializers.SerializerMethodField()

    def get_funding_source_display(self, instance):
        return str(instance.funding_source)

    def get_category_display(self, instance):
        return str(instance.get_category_display())

    def get_project_year_id(self, instance):
        return instance.project_year_id


class MilestoneSerializer(serializers.ModelSerializer):
    target_date = serializers.DateField(format=None, input_formats=None, required=False, allow_null=True)
    class Meta:
        model = models.Milestone
        exclude = ["project_year"]

    latest_update = serializers.SerializerMethodField()
    target_date_display = serializers.SerializerMethodField()
    project_year_id = serializers.SerializerMethodField()

    def get_latest_update(self, instance):
        return instance.latest_update

    def get_target_date_display(self, instance):
        if instance.target_date:
            return instance.target_date.strftime("%Y-%m-%d")

    def get_project_year_id(self, instance):
        return instance.project_year_id
