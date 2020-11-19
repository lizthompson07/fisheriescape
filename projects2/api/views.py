from django.contrib.auth.models import User
from pandas import date_range
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import RetrieveAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from shared_models import models as shared_models
from . import permissions, pagination
from . import serializers
from .. import models, stat_holidays
from ..utils import financial_project_year_summary_data, financial_project_summary_data, get_user_fte_breakdown, can_modify_project, \
    get_manageable_sections
from ..utils import is_management_or_admin


# USER
#######
class CurrentUserAPIView(APIView):
    def get(self, request):
        serializer = serializers.UserDisplaySerializer(instance=request.user)
        data = serializer.data
        if request.query_params.get("project"):
            data.update(can_modify_project(request.user, request.query_params.get("project"), True))
        return Response(data)


class FTEBreakdownAPIView(APIView):
    def get(self, request):
        # if there are no project year ids, do this
        if not request.query_params.get("ids"):
            # if no user is specified, we will assume it is the request user
            if not request.query_params.get("user"):
                my_user = request.user
            else:
                my_user = get_object_or_404(User, pk=request.query_params.get("user"))

            # if there is no fiscal year specified, let's get all years
            if not request.query_params.get("year"):
                # need a list of fiscal years
                fy_qs = shared_models.FiscalYear.objects.filter(projectyear__staff__user=my_user).distinct()
                data = list()
                for fy in fy_qs:
                    data.append(get_user_fte_breakdown(my_user, fiscal_year_id=fy.id))
            else:
                data = get_user_fte_breakdown(my_user, fiscal_year_id=request.query_params.get("year"))
            return Response(data, status.HTTP_200_OK)
        else:
            if not request.query_params.get("year"):
                return Response({"error":"must supply a fiscal year"}, status.HTTP_400_BAD_REQUEST)

            data = list()
            ids = request.query_params.get("ids").split(",")
            year = request.query_params.get("year")
            # now we need a user list for any users in the above list
            users = User.objects.filter(staff_instances2__project_year_id__in=ids).distinct().order_by("last_name")

            for u in users:
                my_dict = get_user_fte_breakdown(u, fiscal_year_id=year)
                data.append(my_dict)


            # project_years =
            return Response(data, status.HTTP_200_OK)

class GetDatesAPIView(APIView):
    def get(self, request):
        fiscal_year = self.request.query_params.get("year")  # to be formatted as follows: YYYY; SAP style
        if fiscal_year:
            fiscal_year = int(fiscal_year)
            # create a pandas date_range object for upcoming fiscal year
            start = f"{fiscal_year - 1}-04-01"
            end = f"{fiscal_year}-03-31"
            datelist = date_range(start=start, end=end).tolist()

            date_format = "%d-%B-%Y"
            short_date_format = "%d-%b-%Y"
            # get a list of statutory holidays
            holiday_list = [d.strftime(date_format) for d in stat_holidays.stat_holiday_list]

            data = list()
            # create a dict for the response
            for dt in datelist:
                is_stat = dt.strftime(date_format) in holiday_list
                weekday = dt.strftime("%A")
                int_weekday = dt.strftime("%w")
                obj = dict(
                    formatted_date=dt.strftime(date_format),
                    formatted_short_date=dt.strftime(short_date_format),
                    weekday=weekday,
                    short_weekday=f'{dt.strftime("%a")}.',
                    int_weekday=int_weekday,
                    is_stat=is_stat,
                    pay_rate=2 if is_stat or int_weekday == 0 else 1.5
                )
                data.append(obj)
            return Response(data, status.HTTP_200_OK)
        raise ValidationError("missing query parameter 'year'")


class ProjectRetrieveAPIView(RetrieveAPIView):
    queryset = models.Project.objects.all().order_by("-created_at")
    serializer_class = serializers.ProjectSerializer
    permission_classes = [permissions.CanModifyOrReadOnly]


class ProjectListAPIView(ListAPIView):
    pagination_class = pagination.StandardResultsSetPagination
    serializer_class = serializers.ProjectSerializer
    permission_classes = [permissions.CanModifyOrReadOnly]

    def get_queryset(self):
        qs = models.Project.objects.order_by("id")
        if not is_management_or_admin(self.request.user):
            qs = qs.filter(is_hidden=False)
        return qs


# PROJECT YEAR
##############

class ProjectYearListAPIView(ListAPIView):
    pagination_class = pagination.StandardResultsSetPagination
    serializer_class = serializers.ProjectYearSerializer
    permission_classes = [permissions.CanModifyOrReadOnly]

    def get_queryset(self):
        qs = models.ProjectYear.objects.order_by("start_date")
        qp = self.request.query_params

        filter_list = [
            "user",
            "is_hidden",
            "title",
            "id",
            'staff',
            'fiscal_year',
            'tag',
            'theme',
            'functional_group',
            'funding_source',
            'region',
            'division',
            'section',
            'status',
        ]
        for filter in filter_list:
            input = qp.get(filter)
            if input == "true":
                input = True
            elif input == "false":
                input = False
            elif input == "null" or input == "":
                input = None

            if input:
                if filter == "user":
                    qs = qs.filter(project__section__in=get_manageable_sections(self.request.user)).order_by("fiscal_year", "project_id")
                elif filter == "is_hidden":
                    qs = qs.filter(project__is_hidden=True)
                elif filter == "status":
                    qs = qs.filter(status=input)
                elif filter == "title":
                    qs = qs.filter(project__title__icontains=input)
                elif filter == "id":
                    qs = qs.filter(project__id=input)
                elif filter == "staff":
                    qs = qs.filter(project__staff_search_field__icontains=input)
                elif filter == "fiscal_year":
                    qs = qs.filter(fiscal_year_id=input)
                elif filter == "tag":
                    qs = qs.filter(project__tags=input)
                elif filter == "theme":
                    qs = qs.filter(project__functional_group__theme_id=input)
                elif filter == "functional_group":
                    qs = qs.filter(project__functional_group_id=input)
                elif filter == "funding_source":
                    qs = qs.filter(project__default_funding_source_id=input)
                elif filter == "region":
                    qs = qs.filter(project__section__division__branch__region_id=input)
                elif filter == "division":
                    qs = qs.filter(project__section__division_id=input)
                elif filter == "section":
                    qs = qs.filter(project__section_id=input)

        # if a regular user is making the request, show only approved projects (and not hidden projects)
        if not is_management_or_admin(self.request.user):
            print(123)
            qs = qs.filter(project__is_hidden=False, status=4)

        return qs.distinct()


class ProjectYearRetrieveAPIView(RetrieveAPIView):
    queryset = models.ProjectYear.objects.all().order_by("-created_at")
    serializer_class = serializers.ProjectYearSerializer
    permission_classes = [permissions.CanModifyOrReadOnly]


class ProjectYearSubmitAPIView(APIView):
    queryset = models.ProjectYear.objects.all().order_by("-created_at")
    serializer_class = serializers.ProjectYearSerializer
    permission_classes = [permissions.CanModifyOrReadOnly]

    def post(self, request, pk):
        project_year = get_object_or_404(models.ProjectYear, pk=pk)
        project_year.submit()
        return Response(serializers.ProjectYearSerializer(project_year).data, status.HTTP_200_OK)


class ProjectYearUnsubmitAPIView(APIView):
    queryset = models.ProjectYear.objects.all().order_by("-created_at")
    serializer_class = serializers.ProjectYearSerializer
    permission_classes = [permissions.CanModifyOrReadOnly]

    def post(self, request, pk):
        project_year = get_object_or_404(models.ProjectYear, pk=pk)
        project_year.unsubmit()
        return Response(serializers.ProjectYearSerializer(project_year).data, status.HTTP_200_OK)


# STAFF
#######
class StaffListCreateAPIView(ListCreateAPIView):
    queryset = models.Staff.objects.all()
    serializer_class = serializers.StaffSerializer
    permission_classes = [permissions.CanModifyOrReadOnly]

    def get_queryset(self):
        year = models.ProjectYear.objects.get(pk=self.kwargs.get("project_year"))
        return year.staff_set.all()

    def perform_create(self, serializer):
        serializer.save(project_year_id=self.kwargs.get("project_year"))

    # def post(self, request, *args, **kwargs):
    #     super().post(request, *args, **kwargs)


class StaffRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = models.Staff.objects.all()
    serializer_class = serializers.StaffSerializer
    permission_classes = [permissions.CanModifyOrReadOnly]


# O&M
#######
class OMCostListCreateAPIView(ListCreateAPIView):
    queryset = models.OMCost.objects.all()
    serializer_class = serializers.OMCostSerializer
    permission_classes = [permissions.CanModifyOrReadOnly]

    def get_queryset(self):
        year = models.ProjectYear.objects.get(pk=self.kwargs.get("project_year"))
        return year.omcost_set.all()

    def perform_create(self, serializer):
        serializer.save(project_year_id=self.kwargs.get("project_year"))

    # def post(self, request, *args, **kwargs):
    #     super().post(request, *args, **kwargs)


class OMCostRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = models.OMCost.objects.all()
    serializer_class = serializers.OMCostSerializer
    permission_classes = [permissions.CanModifyOrReadOnly]


class AddAllCostsAPIView(APIView):
    permission_classes = [permissions.CanModifyOrReadOnly]

    def post(self, request, project_year):
        year = models.ProjectYear.objects.get(pk=self.kwargs.get("project_year"))
        year.add_all_om_costs()
        serializer = serializers.OMCostSerializer(instance=year.omcost_set.all(), many=True)
        return Response(serializer.data, status.HTTP_200_OK)


class RemoveEmptyCostsAPIView(APIView):
    permission_classes = [permissions.CanModifyOrReadOnly]

    def post(self, request, project_year):
        year = models.ProjectYear.objects.get(pk=self.kwargs.get("project_year"))
        year.clear_empty_om_costs()
        serializer = serializers.OMCostSerializer(instance=year.omcost_set.all(), many=True)
        return Response(serializer.data, status.HTTP_200_OK)


# CAPITAL
#########
class CapitalCostListCreateAPIView(ListCreateAPIView):
    queryset = models.CapitalCost.objects.all()
    serializer_class = serializers.CapitalCostSerializer
    permission_classes = [permissions.CanModifyOrReadOnly]

    def get_queryset(self):
        year = models.ProjectYear.objects.get(pk=self.kwargs.get("project_year"))
        return year.capitalcost_set.all()

    def perform_create(self, serializer):
        serializer.save(project_year_id=self.kwargs.get("project_year"))


class CapitalCostRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = models.CapitalCost.objects.all()
    serializer_class = serializers.CapitalCostSerializer
    permission_classes = [permissions.CanModifyOrReadOnly]


# GC
####

class GCCostListCreateAPIView(ListCreateAPIView):
    queryset = models.GCCost.objects.all()
    serializer_class = serializers.GCCostSerializer
    permission_classes = [permissions.CanModifyOrReadOnly]

    def get_queryset(self):
        year = models.ProjectYear.objects.get(pk=self.kwargs.get("project_year"))
        return year.gc_costs.all()

    def perform_create(self, serializer):
        serializer.save(project_year_id=self.kwargs.get("project_year"))


class GCCostRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = models.GCCost.objects.all()
    serializer_class = serializers.GCCostSerializer
    permission_classes = [permissions.CanModifyOrReadOnly]


# MILESTONE
###########
class MilestoneListCreateAPIView(ListCreateAPIView):
    queryset = models.Milestone.objects.all()
    serializer_class = serializers.MilestoneSerializer
    permission_classes = [permissions.CanModifyOrReadOnly]

    def get_queryset(self):
        year = models.ProjectYear.objects.get(pk=self.kwargs.get("project_year"))
        return year.milestones.all()

    def perform_create(self, serializer):
        serializer.save(project_year_id=self.kwargs.get("project_year"))


class MilestoneRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = models.Milestone.objects.all()
    serializer_class = serializers.MilestoneSerializer
    permission_classes = [permissions.CanModifyOrReadOnly]


# COLLABORATOR
##############
class CollaboratorListCreateAPIView(ListCreateAPIView):
    queryset = models.Collaborator.objects.all()
    serializer_class = serializers.CollaboratorSerializer
    permission_classes = [permissions.CanModifyOrReadOnly]

    def get_queryset(self):
        year = models.ProjectYear.objects.get(pk=self.kwargs.get("project_year"))
        return year.collaborators.all()

    def perform_create(self, serializer):
        serializer.save(project_year_id=self.kwargs.get("project_year"))


class CollaboratorRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = models.Collaborator.objects.all()
    serializer_class = serializers.CollaboratorSerializer
    permission_classes = [permissions.CanModifyOrReadOnly]


# AGREEMENTS
##############
class AgreementListCreateAPIView(ListCreateAPIView):
    queryset = models.CollaborativeAgreement.objects.all()
    serializer_class = serializers.AgreementSerializer
    permission_classes = [permissions.CanModifyOrReadOnly]

    def get_queryset(self):
        year = models.ProjectYear.objects.get(pk=self.kwargs.get("project_year"))
        return year.agreements.all()

    def perform_create(self, serializer):
        serializer.save(project_year_id=self.kwargs.get("project_year"))


class AgreementRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = models.CollaborativeAgreement.objects.all()
    serializer_class = serializers.AgreementSerializer
    permission_classes = [permissions.CanModifyOrReadOnly]


# FILES / Supporting Resources
##############
class FileListCreateAPIView(ListCreateAPIView):
    queryset = models.File.objects.all()
    serializer_class = serializers.FileSerializer
    permission_classes = [permissions.CanModifyOrReadOnly]

    def get_queryset(self):
        year = models.ProjectYear.objects.get(pk=self.kwargs.get("project_year"))
        return year.files.all()

    def perform_create(self, serializer):
        year = models.ProjectYear.objects.get(pk=self.kwargs.get("project_year"))
        serializer.save(project=year.project, project_year=year)

        if self.request.FILES:
            print(self.request.FILES)


class FileRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = models.File.objects.all()
    serializer_class = serializers.FileSerializer
    permission_classes = [permissions.CanModifyOrReadOnly]


# FINANCIALS
############


class FinancialsAPIView(APIView):
    permissions = [IsAuthenticated]

    def get(self, request, project_year=None, project=None):
        if not project_year and not project:
            return Response(None, status.HTTP_400_BAD_REQUEST)

        if project_year:
            obj = get_object_or_404(models.ProjectYear, pk=project_year)
            data = financial_project_year_summary_data(obj)

        else:  # must be supplied with a project
            obj = get_object_or_404(models.Project, pk=project)
            data = financial_project_summary_data(obj)

        return Response(data, status.HTTP_200_OK)


# LOOKUPS
##########


class FiscalYearListAPIView(ListAPIView):
    serializer_class = serializers.FiscalYearSerializer
    permission_classes = [permissions.CanModifyOrReadOnly]

    def get_queryset(self):
        qs = shared_models.FiscalYear.objects.filter(projectyear__isnull=False)

        if self.request.query_params.get("user") == 'true':
            qs = qs.filter(projectyear__project__section__in=get_manageable_sections(self.request.user))

        return qs.distinct()


class TagListAPIView(ListAPIView):
    serializer_class = serializers.TagSerializer
    permission_classes = [permissions.CanModifyOrReadOnly]

    def get_queryset(self):
        qs = models.Tag.objects.filter(projects__isnull=False)

        if self.request.query_params.get("user") == 'true':
            qs = qs.filter(projects__section__in=get_manageable_sections(self.request.user))

        return qs.distinct()

class ThemeListAPIView(ListAPIView):
    serializer_class = serializers.ThemeSerializer
    permission_classes = [permissions.CanModifyOrReadOnly]

    def get_queryset(self):
        qs = models.Theme.objects.all()
        if self.request.query_params.get("user") == 'true':
            qs = qs.filter(functional_groups__projects__section__in=get_manageable_sections(self.request.user))
        return qs.distinct()


class FunctionalGroupListAPIView(ListAPIView):
    serializer_class = serializers.FunctionalGroupSerializer
    permission_classes = [permissions.CanModifyOrReadOnly]


    def get_queryset(self):
        qs = models.FunctionalGroup.objects.all()

        if self.request.query_params.get("section"):
            qs = qs.filter(sections=self.request.query_params.get("section"))
        elif self.request.query_params.get("user") == 'true':
            qs = qs.filter(sections__in=get_manageable_sections(self.request.user))
        elif self.request.query_params.get("division"):
            qs = qs.filter(sections__division=self.request.query_params.get("division"))
        elif self.request.query_params.get("region"):
            qs = qs.filter(sections__division__branch__region=self.request.query_params.get("region"))
        return qs.distinct()


class FundingSourceListAPIView(ListAPIView):
    serializer_class = serializers.FundingSourceSerializer
    permission_classes = [permissions.CanModifyOrReadOnly]

    def get_queryset(self):
        qs = models.FundingSource.objects.all()
        if self.request.query_params.get("user") == 'true':
            qs = qs.filter(projects__section__in=get_manageable_sections(self.request.user))
        return qs.distinct()


class RegionListAPIView(ListAPIView):
    serializer_class = serializers.RegionSerializer
    permission_classes = [permissions.CanModifyOrReadOnly]

    def get_queryset(self):
        qs = shared_models.Region.objects.filter(branches__divisions__sections__projects2__isnull=False).distinct()
        return qs


class DivisionListAPIView(ListAPIView):
    serializer_class = serializers.DivisionSerializer
    permission_classes = [permissions.CanModifyOrReadOnly]

    def get_queryset(self):
        qs = shared_models.Division.objects.filter(sections__projects2__isnull=False).distinct()
        if self.request.query_params.get("region"):
            qs = qs.filter(branch__region_id=self.request.query_params.get("region"))
        return qs


class SectionListAPIView(ListAPIView):
    serializer_class = serializers.SectionSerializer
    permission_classes = [permissions.CanModifyOrReadOnly]

    def get_queryset(self):
        qs = shared_models.Section.objects.filter(projects2__isnull=False).distinct()
        if self.request.query_params.get("division"):
            qs = qs.filter(division_id=self.request.query_params.get("division"))
        elif self.request.query_params.get("region"):
            qs = qs.filter(division__branch__region_id=self.request.query_params.get("region"))
        elif self.request.query_params.get("user"):
            qs = get_manageable_sections(self.request.user)
        return qs
