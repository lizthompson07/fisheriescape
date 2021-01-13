from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import permissions
from . import serializers
from .. import models


# USER
#######
class CurrentUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = serializers.UserDisplaySerializer(instance=request.user)
        data = serializer.data
        return Response(data)


# Observations
##############

class ObservationListCreateAPIView(ListCreateAPIView):
    serializer_class = serializers.ObservationSerializer
    permission_classes = [permissions.ScubaCRUDOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(section_id=self.request.data["section_id"])

    def get_queryset(self):
        qs = models.Observation.objects.order_by("section", "id")
        qp = self.request.query_params

        if qp.get("dive"):
            dive = get_object_or_404(models.Dive, pk=qp.get("dive"))
            qs = qs.filter(section__dive=dive)

        return qs


class ObservationRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = models.Observation.objects.all()
    serializer_class = serializers.ObservationSerializer
    permission_classes = [permissions.ScubaCRUDOrReadOnly]


# Sections
##############

class SectionListCreateAPIView(ListCreateAPIView):
    serializer_class = serializers.SectionSerializer
    permission_classes = [permissions.ScubaCRUDOrReadOnly]

    def get_queryset(self):
        qs = models.Section.objects.order_by("dive", "interval")
        qp = self.request.query_params

        if qp.get("dive"):
            dive = get_object_or_404(models.Dive, pk=qp.get("dive"))
            qs = qs.filter(dive=dive)

        return qs


class SectionRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = models.Section.objects.all()
    serializer_class = serializers.SectionSerializer
    permission_classes = [permissions.ScubaCRUDOrReadOnly]
#
# class ProjectYearRetrieveAPIView(RetrieveAPIView):
#     queryset = models.ProjectYear.objects.all().order_by("-created_at")
#     serializer_class = serializers.ProjectYearSerializer
#     permission_classes = [permissions.CanModifyOrReadOnly]
#
#
# class ProjectYearSubmitAPIView(APIView):
#     queryset = models.ProjectYear.objects.all().order_by("-created_at")
#     serializer_class = serializers.ProjectYearSerializer
#     permission_classes = [permissions.CanModifyOrReadOnly]
#
#     def post(self, request, project_year):
#         project_year = get_object_or_404(models.ProjectYear, pk=project_year)
#         project_year.submit()
#
#         # create a new email object
#         email = emails.ProjectYearSubmissionEmail(project_year, request)
#         # send the email object
#         custom_send_mail(
#             subject=email.subject,
#             html_message=email.message,
#             from_email=email.from_email,
#             recipient_list=email.to_list
#         )
#
#         return Response(serializers.ProjectYearSerializer(project_year).data, status.HTTP_200_OK)
#
#
# class ProjectYearUnsubmitAPIView(APIView):
#     queryset = models.ProjectYear.objects.all().order_by("-created_at")
#     serializer_class = serializers.ProjectYearSerializer
#     permission_classes = [permissions.CanModifyOrReadOnly]
#
#     def post(self, request, project_year):
#         project_year = get_object_or_404(models.ProjectYear, pk=project_year)
#         project_year.unsubmit()
#         return Response(serializers.ProjectYearSerializer(project_year).data, status.HTTP_200_OK)
#
#
# # STAFF
# #######
# class StaffListCreateAPIView(ListCreateAPIView):
#     queryset = models.Staff.objects.all()
#     serializer_class = serializers.StaffSerializer
#     permission_classes = [permissions.CanModifyOrReadOnly]
#
#     def get_queryset(self):
#         year = models.ProjectYear.objects.get(pk=self.kwargs.get("project_year"))
#         return year.staff_set.all()
#
#     def perform_create(self, serializer):
#         serializer.save(project_year_id=self.kwargs.get("project_year"))
#
#     # def post(self, request, *args, **kwargs):
#     #     super().post(request, *args, **kwargs)
#
#
# class StaffRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
#     queryset = models.Staff.objects.all()
#     serializer_class = serializers.StaffSerializer
#     permission_classes = [permissions.CanModifyOrReadOnly]
#
#
# # O&M
# #######
# class OMCostListCreateAPIView(ListCreateAPIView):
#     queryset = models.OMCost.objects.all()
#     serializer_class = serializers.OMCostSerializer
#     permission_classes = [permissions.CanModifyOrReadOnly]
#
#     def get_queryset(self):
#         year = models.ProjectYear.objects.get(pk=self.kwargs.get("project_year"))
#         return year.omcost_set.all()
#
#     def perform_create(self, serializer):
#         serializer.save(project_year_id=self.kwargs.get("project_year"))
#
#     # def post(self, request, *args, **kwargs):
#     #     super().post(request, *args, **kwargs)
#
#
# class OMCostRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
#     queryset = models.OMCost.objects.all()
#     serializer_class = serializers.OMCostSerializer
#     permission_classes = [permissions.CanModifyOrReadOnly]
#
#
# class AddAllCostsAPIView(APIView):
#     permission_classes = [permissions.CanModifyOrReadOnly]
#
#     def post(self, request, project_year):
#         year = models.ProjectYear.objects.get(pk=self.kwargs.get("project_year"))
#         year.add_all_om_costs()
#         serializer = serializers.OMCostSerializer(instance=year.omcost_set.all(), many=True)
#         return Response(serializer.data, status.HTTP_200_OK)
#
#
# class RemoveEmptyCostsAPIView(APIView):
#     permission_classes = [permissions.CanModifyOrReadOnly]
#
#     def post(self, request, project_year):
#         year = models.ProjectYear.objects.get(pk=self.kwargs.get("project_year"))
#         year.clear_empty_om_costs()
#         serializer = serializers.OMCostSerializer(instance=year.omcost_set.all(), many=True)
#         return Response(serializer.data, status.HTTP_200_OK)
#
#
# # CAPITAL
# #########
# class CapitalCostListCreateAPIView(ListCreateAPIView):
#     queryset = models.CapitalCost.objects.all()
#     serializer_class = serializers.CapitalCostSerializer
#     permission_classes = [permissions.CanModifyOrReadOnly]
#
#     def get_queryset(self):
#         year = models.ProjectYear.objects.get(pk=self.kwargs.get("project_year"))
#         return year.capitalcost_set.all()
#
#     def perform_create(self, serializer):
#         serializer.save(project_year_id=self.kwargs.get("project_year"))
#
#
# class CapitalCostRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
#     queryset = models.CapitalCost.objects.all()
#     serializer_class = serializers.CapitalCostSerializer
#     permission_classes = [permissions.CanModifyOrReadOnly]
#
#
# # GC
# ####
#
# class GCCostListCreateAPIView(ListCreateAPIView):
#     queryset = models.GCCost.objects.all()
#     serializer_class = serializers.GCCostSerializer
#     permission_classes = [permissions.CanModifyOrReadOnly]
#
#     def get_queryset(self):
#         year = models.ProjectYear.objects.get(pk=self.kwargs.get("project_year"))
#         return year.gc_costs.all()
#
#     def perform_create(self, serializer):
#         serializer.save(project_year_id=self.kwargs.get("project_year"))
#
#
# class GCCostRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
#     queryset = models.GCCost.objects.all()
#     serializer_class = serializers.GCCostSerializer
#     permission_classes = [permissions.CanModifyOrReadOnly]
#
#
# # MILESTONE
# ###########
# class ActivityListCreateAPIView(ListCreateAPIView):
#     queryset = models.Activity.objects.all()
#     serializer_class = serializers.ActivitySerializer
#     permission_classes = [permissions.CanModifyOrReadOnly]
#
#     def get_queryset(self):
#         year = models.ProjectYear.objects.get(pk=self.kwargs.get("project_year"))
#         return year.activities.all()
#
#     def perform_create(self, serializer):
#         serializer.save(project_year_id=self.kwargs.get("project_year"))
#
#
# class ActivityRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
#     queryset = models.Activity.objects.all()
#     serializer_class = serializers.ActivitySerializer
#     permission_classes = [permissions.CanModifyOrReadOnly]
#
#
# # COLLABORATOR
# ##############
# class CollaboratorListCreateAPIView(ListCreateAPIView):
#     queryset = models.Collaborator.objects.all()
#     serializer_class = serializers.CollaboratorSerializer
#     permission_classes = [permissions.CanModifyOrReadOnly]
#
#     def get_queryset(self):
#         year = models.ProjectYear.objects.get(pk=self.kwargs.get("project_year"))
#         return year.collaborators.all()
#
#     def perform_create(self, serializer):
#         serializer.save(project_year_id=self.kwargs.get("project_year"))
#
#
# class CollaboratorRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
#     queryset = models.Collaborator.objects.all()
#     serializer_class = serializers.CollaboratorSerializer
#     permission_classes = [permissions.CanModifyOrReadOnly]
#
#
# # AGREEMENTS
# ##############
# class AgreementListCreateAPIView(ListCreateAPIView):
#     queryset = models.CollaborativeAgreement.objects.all()
#     serializer_class = serializers.AgreementSerializer
#     permission_classes = [permissions.CanModifyOrReadOnly]
#
#     def get_queryset(self):
#         year = models.ProjectYear.objects.get(pk=self.kwargs.get("project_year"))
#         return year.agreements.all()
#
#     def perform_create(self, serializer):
#         serializer.save(project_year_id=self.kwargs.get("project_year"))
#
#
# class AgreementRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
#     queryset = models.CollaborativeAgreement.objects.all()
#     serializer_class = serializers.AgreementSerializer
#     permission_classes = [permissions.CanModifyOrReadOnly]
#
#
# # STATUS REPORTS
# ##############
#
# class StatusReportListCreateAPIView(ListCreateAPIView):
#     queryset = models.StatusReport.objects.all()
#     serializer_class = serializers.StatusReportSerializer
#     permission_classes = [permissions.CanModifyOrReadOnly]
#
#     def get_queryset(self):
#         year = models.ProjectYear.objects.get(pk=self.kwargs.get("project_year"))
#         return year.reports.all()
#
#     def perform_create(self, serializer):
#         serializer.save(project_year_id=self.kwargs.get("project_year"))
#
#
# class StatusReportRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
#     queryset = models.StatusReport.objects.all()
#     serializer_class = serializers.StatusReportSerializer
#     permission_classes = [permissions.CanModifyOrReadOnly]
#
#     def perform_update(self, serializer):
#         serializer.save(modified_by=self.request.user)
#
#
# # Activity Updates
#
#
# class ActivityUpdateListAPIView(ListAPIView):
#     queryset = models.StatusReport.objects.all()
#     serializer_class = serializers.ActivityUpdateSerializer
#     permission_classes = [permissions.CanModifyOrReadOnly]
#
#     def get_queryset(self):
#         status_report = get_object_or_404(models.StatusReport, pk=self.kwargs.get("status_report"))
#         return status_report.updates.all()
#
#
# class ActivityUpdateRetrieveUpdateAPIView(RetrieveUpdateAPIView):
#     queryset = models.ActivityUpdate.objects.all()
#     serializer_class = serializers.ActivityUpdateSerializer
#     permission_classes = [permissions.CanModifyOrReadOnly]
#
#
# # FILES / Supporting Resources
# ##############
# class FileListCreateAPIView(ListCreateAPIView):
#     queryset = models.File.objects.all()
#     serializer_class = serializers.FileSerializer
#     permission_classes = [permissions.CanModifyOrReadOnly]
#
#     def get_queryset(self):
#         year = models.ProjectYear.objects.get(pk=self.kwargs.get("project_year"))
#         qs = year.files.all()
#
#         qp = self.request.query_params
#         if qp.get("status_report"):
#             qs = qs.filter(status_report=qp.get("status_report"))
#
#         return qs
#
#     def perform_create(self, serializer):
#         year = get_object_or_404(models.ProjectYear, pk=self.kwargs.get("project_year"))
#         kwargs = dict(project=year.project, project_year=year)
#         qp = self.request.query_params
#         if qp.get("status_report"):
#             kwargs["status_report_id"] = qp.get("status_report")
#         serializer.save(**kwargs)
#
#
# class FileRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
#     queryset = models.File.objects.all()
#     serializer_class = serializers.FileSerializer
#     permission_classes = [permissions.CanModifyOrReadOnly]
#
#
# # FINANCIALS
# ############
#
#
# class FinancialsAPIView(APIView):
#     permissions = [IsAuthenticated]
#
#     def get(self, request, project_year=None, project=None):
#         if not project_year and not project:
#             # the we will be needing ids and year query_params
#             qp = request.query_params
#             if not qp.get("ids"):
#                 return Response(None, status.HTTP_400_BAD_REQUEST)
#             else:
#
#                 ids = request.query_params.get("ids").split(",")
#
#                 # get project year list
#                 project_years = models.ProjectYear.objects.filter(id__in=ids)
#                 data = multiple_financial_project_year_summary_data(project_years)
#                 return Response(data, status.HTTP_200_OK)
#
#         if project_year:
#             obj = get_object_or_404(models.ProjectYear, pk=project_year)
#             data = financial_project_year_summary_data(obj)
#
#         else:  # must be supplied with a project
#             obj = get_object_or_404(models.Project, pk=project)
#             data = financial_project_summary_data(obj)
#
#         return Response(data, status.HTTP_200_OK)
#
#
# # LOOKUPS
# ##########
#
#
# class FiscalYearListAPIView(ListAPIView):
#     serializer_class = serializers.FiscalYearSerializer
#     permission_classes = [permissions.CanModifyOrReadOnly]
#
#     def get_queryset(self):
#         qs = shared_models.FiscalYear.objects.filter(projectyear__isnull=False)
#
#         if self.request.query_params.get("user") == 'true':
#             qs = qs.filter(projectyear__project__section__in=get_manageable_sections(self.request.user))
#
#         return qs.distinct()
#
#
# class TagListAPIView(ListAPIView):
#     serializer_class = serializers.TagSerializer
#     permission_classes = [permissions.CanModifyOrReadOnly]
#
#     def get_queryset(self):
#         qs = models.Tag.objects.filter(projects__isnull=False)
#
#         if self.request.query_params.get("user") == 'true':
#             qs = qs.filter(projects__section__in=get_manageable_sections(self.request.user))
#
#         return qs.distinct()
#
#
# class ThemeListAPIView(ListAPIView):
#     serializer_class = serializers.ThemeSerializer
#     permission_classes = [permissions.CanModifyOrReadOnly]
#
#     def get_queryset(self):
#         qs = models.Theme.objects.all()
#         if self.request.query_params.get("user") == 'true':
#             qs = qs.filter(functional_groups__projects__section__in=get_manageable_sections(self.request.user))
#         return qs.distinct()
#
#
# class FunctionalGroupListAPIView(ListAPIView):
#     serializer_class = serializers.FunctionalGroupSerializer
#     permission_classes = [permissions.CanModifyOrReadOnly]
#
#     def get_queryset(self):
#         qs = models.FunctionalGroup.objects.all()
#
#         if self.request.query_params.get("section"):
#             qs = qs.filter(sections=self.request.query_params.get("section"))
#         elif self.request.query_params.get("user") == 'true':
#             qs = qs.filter(sections__in=get_manageable_sections(self.request.user))
#         elif self.request.query_params.get("division"):
#             qs = qs.filter(sections__division=self.request.query_params.get("division"))
#         elif self.request.query_params.get("region"):
#             qs = qs.filter(sections__division__branch__region=self.request.query_params.get("region"))
#         return qs.distinct()
#
#
# class FundingSourceListAPIView(ListAPIView):
#     serializer_class = serializers.FundingSourceSerializer
#     permission_classes = [permissions.CanModifyOrReadOnly]
#
#     def get_queryset(self):
#         qs = models.FundingSource.objects.all()
#         if self.request.query_params.get("user") == 'true':
#             qs = qs.filter(projects__section__in=get_manageable_sections(self.request.user))
#         return qs.distinct()
#
#
# class RegionListAPIView(ListAPIView):
#     serializer_class = serializers.RegionSerializer
#     permission_classes = [permissions.CanModifyOrReadOnly]
#
#     def get_queryset(self):
#         qs = shared_models.Region.objects.filter(branches__divisions__sections__projects2__isnull=False)
#
#         # if there is a user param, further filter qs to what user can access
#         if self.request.query_params.get("user"):
#             qs = qs.filter(branches__divisions__sections__in=get_manageable_sections(self.request.user))
#         return qs.distinct()
#
#
# class DivisionListAPIView(ListAPIView):
#     serializer_class = serializers.DivisionSerializer
#     permission_classes = [permissions.CanModifyOrReadOnly]
#
#     def get_queryset(self):
#         qs = shared_models.Division.objects.filter(sections__projects2__isnull=False).distinct()
#         # if there is a user param, further filter qs to what user can access
#         if self.request.query_params.get("user"):
#             qs = qs.filter(sections__in=get_manageable_sections(self.request.user))
#
#         if self.request.query_params.get("region"):
#             qs = qs.filter(branch__region_id=self.request.query_params.get("region"))
#
#         return qs.distinct()
#
#
# class SectionListAPIView(ListAPIView):
#     serializer_class = serializers.SectionSerializer
#     permission_classes = [permissions.CanModifyOrReadOnly]
#
#     def get_queryset(self):
#         qs = shared_models.Section.objects.filter(projects2__isnull=False).distinct()
#         if self.request.query_params.get("division"):
#             qs = qs.filter(division_id=self.request.query_params.get("division"))
#         elif self.request.query_params.get("region"):
#             qs = qs.filter(division__branch__region_id=self.request.query_params.get("region"))
#
#         # if there is a user param, further filter qs to what user can access
#         if self.request.query_params.get("user"):
#             qs = qs.filter(id__in=[s.id for s in get_manageable_sections(self.request.user)])
#         return qs
#
#
# # Reviews
# ##############
# class ReviewListCreateAPIView(ListCreateAPIView):
#     queryset = models.Review.objects.all()
#     serializer_class = serializers.ReviewSerializer
#     permission_classes = [permissions.CanModifyOrReadOnly]
#
#     def get_queryset(self):
#         year = models.ProjectYear.objects.get(pk=self.kwargs.get("project_year"))
#         return year.agreements.all()
#
#     def perform_create(self, serializer):
#         my_review = serializer.save(
#             project_year_id=self.kwargs.get("project_year"),
#             last_modified_by=self.request.user
#         )
#
#         if self.request.data.get("email_update"):
#             my_review.send_approval_email(self.request)
#
#
# class ReviewRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
#     queryset = models.Review.objects.all()
#     serializer_class = serializers.ReviewSerializer
#     permission_classes = [permissions.CanModifyOrReadOnly]
#
#     def perform_update(self, serializer):
#         my_review = serializer.save(
#             last_modified_by=self.request.user
#         )
#
#
#
#         if self.request.data.get("email_update"):
#             my_review.send_approval_email(self.request)
#
