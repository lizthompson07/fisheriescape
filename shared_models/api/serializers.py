from django.contrib.auth.models import User, Group
from rest_framework import serializers

from shared_models.models import FiscalYear, Region, Division, Section, Person, Branch, Sector


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["id", "name", ]


class CurrentUserSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "username",
            "email",
            "groups",
        ]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "username",
            "full_name"
        ]

    full_name = serializers.SerializerMethodField()

    def get_full_name(self, instance):
        return instance.get_full_name()


class FiscalYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = FiscalYear
        fields = "__all__"


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = "__all__"

    metadata = serializers.SerializerMethodField()

    def get_metadata(self, instance):
        return instance.metadata


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = "__all__"

    sector_obj = serializers.SerializerMethodField()
    region_obj = serializers.SerializerMethodField()  # should eventually be deleted
    head_display = serializers.SerializerMethodField()
    admin_display = serializers.SerializerMethodField()
    metadata = serializers.SerializerMethodField()
    display = serializers.SerializerMethodField()

    def get_display(self, instance):
        return str(instance)

    def get_metadata(self, instance):
        return instance.metadata

    def get_admin_display(self, instance):
        if instance.admin:
            return instance.admin.get_full_name()

    def get_head_display(self, instance):
        if instance.head:
            return instance.head.get_full_name()

    def get_region_obj(self, instance):
        return RegionSerializer(instance.region).data

    def get_sector_obj(self, instance):
        return SectorSerializer(instance.sector).data


class SectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sector
        fields = "__all__"

    region_obj = serializers.SerializerMethodField()
    head_display = serializers.SerializerMethodField()
    admin_display = serializers.SerializerMethodField()
    metadata = serializers.SerializerMethodField()
    display = serializers.SerializerMethodField()

    def get_display(self, instance):
        return str(instance)

    def get_metadata(self, instance):
        return instance.metadata

    def get_admin_display(self, instance):
        if instance.admin:
            return instance.admin.get_full_name()

    def get_head_display(self, instance):
        if instance.head:
            return instance.head.get_full_name()

    def get_region_obj(self, instance):
        return RegionSerializer(instance.region).data


class DivisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Division
        fields = "__all__"

    display = serializers.SerializerMethodField()
    branch_obj = serializers.SerializerMethodField()
    head_display = serializers.SerializerMethodField()
    admin_display = serializers.SerializerMethodField()
    metadata = serializers.SerializerMethodField()

    def get_metadata(self, instance):
        return instance.metadata

    def get_admin_display(self, instance):
        if instance.admin:
            return instance.admin.get_full_name()

    def get_head_display(self, instance):
        if instance.head:
            return instance.head.get_full_name()

    def get_branch_obj(self, instance):
        return BranchSerializer(instance.branch).data

    def get_display(self, instance):
        return str(instance)


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = "__all__"

    full_name = serializers.SerializerMethodField()
    tname = serializers.SerializerMethodField()
    division_obj = serializers.SerializerMethodField()
    head_display = serializers.SerializerMethodField()
    admin_display = serializers.SerializerMethodField()
    metadata = serializers.SerializerMethodField()

    def get_metadata(self, instance):
        return instance.metadata

    def get_admin_display(self, instance):
        if instance.admin:
            return instance.admin.get_full_name()

    def get_head_display(self, instance):
        if instance.head:
            return instance.head.get_full_name()

    def get_division_obj(self, instance):
        return DivisionSerializer(instance.division).data

    def get_tname(self, instance):
        return instance.tname

    def get_full_name(self, instance):
        return instance.full_name


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = "__all__"

    full_name = serializers.SerializerMethodField()
    tposition = serializers.SerializerMethodField()

    def get_tposition(self, instance):
        return instance.tposition

    def get_full_name(self, instance):
        return instance.full_name
