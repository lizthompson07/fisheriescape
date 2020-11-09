from django.contrib.auth.models import User
from rest_framework import serializers

from projects2.models import ProjectYear


class UserDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username"]


class ProjectYearSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProjectYear
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