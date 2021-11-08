from copy import deepcopy

from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import gettext as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from shared_models.api.views import _get_labels
from shared_models.models import Section, Organization
from . import serializers
from .permissions import CanModifyApplicationOrReadOnly
from .. import models, utils, model_choices, emails


# USER
#######
from ..utils import achievements_summary_table


class CurrentUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = serializers.UserDisplaySerializer(instance=request.user)
        data = serializer.data
        qp = request.GET
        data["is_admin"] = utils.in_res_admin_group(request.user)
        if qp.get("application"):
            data["can_modify"] = utils.can_modify_application(request.user, qp.get("application"), return_as_dict=True)
            data["can_modify_recommendation"] = utils.can_modify_recommendation(request.user, qp.get("application"), return_as_dict=True)
            data["is_manager"] = utils.is_manager(request.user, qp.get("application"))
            data["is_applicant"] = utils.is_applicant(request.user, qp.get("application"))
        return Response(data)


class ApplicationViewSet(ModelViewSet):
    serializer_class = serializers.ApplicationSerializer
    permission_classes = [CanModifyApplicationOrReadOnly]
    queryset = models.Application.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        'section__division__branch__sector__region',
        "section__division__branch__sector",
        "section__division__branch",
        "section__division",
        "section",
        "fiscal_year",
        "status",
    ]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class RecommendationViewSet(ModelViewSet):
    serializer_class = serializers.RecommendationSerializer
    # permission_classes = [CanModifyApplicationOrReadOnly]
    queryset = models.Recommendation.objects.all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def post(self, request, pk):
        qp = request.query_params
        recommendation = get_object_or_404(models.Recommendation, pk=pk)
        if qp.get("sign-by-manager"):
            """
            we have to make sure this user is allowed to sign:
            - they must be the correct person
            - application must be submitted
            - recommendation fields must be complete
            - should not have already happened
            """
            if not recommendation.application.manager == request.user:
                raise ValidationError(_("Sorry, you are not the right person to be recommending this application. We were expecting:") +
                                      f"{recommendation.application.manager}")
            elif not (recommendation.decision and recommendation.recommendation_text):
                raise ValidationError(_("You must provide recommendation text and a decision before signing."))
            elif not recommendation.application.submission_date:
                raise ValidationError(_("You can only sign a recommendation for an application that has been submitted."))
            elif recommendation.manager_signed:
                raise ValidationError(_("You have already signed this recommendation."))
            recommendation.manager_signed_by = request.user
            recommendation.manager_signed = timezone.now()
            recommendation.save()
            email = emails.SignatureAwaitingEmail(request, recommendation)
            email.send()
            return Response(serializers.RecommendationSerializer(recommendation).data, status.HTTP_200_OK)
        elif qp.get("sign-by-applicant"):
            """
            we have to make sure this user is allowed to sign:
            - they must be the correct person
            - application must be submitted
            - must be signed by the manager
            - should not have already happened
            """
            if not recommendation.application.applicant == request.user:
                raise ValidationError(_("Sorry, you are not the right person to be signing. We were expecting:") +
                                      f"{recommendation.application.manager}")
            elif not recommendation.application.submission_date:
                raise ValidationError(_("You can only sign a recommendation for an application that has been submitted."))
            elif not recommendation.manager_signed:
                raise ValidationError(_("Your manager has not yet signed this recommendation."))
            elif recommendation.applicant_signed:
                raise ValidationError(_("You have already signed this recommendation."))
            recommendation.applicant_signed_by = request.user
            recommendation.applicant_signed = timezone.now()
            recommendation.applicant_comment = request.data.get("applicant_comment")
            recommendation.save()
            return Response(serializers.RecommendationSerializer(recommendation).data, status.HTTP_200_OK)

        raise ValidationError(_("This endpoint cannot be used without a query param"))


class ApplicationOutcomeViewSet(ModelViewSet):
    queryset = models.ApplicationOutcome.objects.all()
    serializer_class = serializers.ApplicationOutcomeSerializer
    permission_classes = [CanModifyApplicationOrReadOnly]

    def list(self, request, *args, **kwargs):
        qp = request.query_params
        if qp.get("application"):
            application = get_object_or_404(models.Application, pk=qp.get("application"))
            qs = application.outcomes.all()
            serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data)
        raise ValidationError(_("You need to specify a RES application"))

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class AchievementViewSet(ModelViewSet):
    queryset = models.Achievement.objects.all()
    serializer_class = serializers.AchievementSerializer
    permission_classes = [CanModifyApplicationOrReadOnly]
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['detail']
    filterset_fields = [
        'user',
    ]

    def list(self, request, *args, **kwargs):
        qp = request.query_params
        if qp.get("summary-table"):
            if not qp.get("user"):
                raise ValidationError(_("Cannot run summary without user param."))
            user = get_object_or_404(User, pk=qp.get("user"))
            data = achievements_summary_table(user)
            print(data)
            return Response(data)
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def post(self, request, pk):
        qp = request.query_params
        old_achievement = get_object_or_404(models.Achievement, pk=pk)
        if qp.get("clone"):
            new_achievement = deepcopy(old_achievement)
            new_achievement.pk = None
            new_achievement.detail = "CLONED " + new_achievement.detail
            new_achievement.save()
            return Response(serializers.AchievementSerializer(new_achievement).data, status.HTTP_200_OK)

        raise ValidationError(_("This endpoint cannot be used without a query param"))


class ContextListAPIView(ListAPIView):
    queryset = models.Context.objects.all()
    serializer_class = serializers.ContextSerializer
    permission_classes = [IsAuthenticated]


class AchievementCategoryListAPIView(ListAPIView):
    queryset = models.AchievementCategory.objects.all()
    serializer_class = serializers.AchievementCategorySerializer
    permission_classes = [IsAuthenticated]


class ApplicationModelMetaAPIView(APIView):
    permission_classes = [IsAuthenticated]
    model = models.Application

    def get(self, request):
        data = dict()
        data['labels'] = _get_labels(self.model)
        data['applicant_choices'] = [dict(text=f"{c.last_name}, {c.first_name}", value=c.id) for c in User.objects.order_by("last_name", "first_name")]
        data['group_level_choices'] = [dict(text=str(c), value=c.id) for c in models.GroupLevel.objects.all()]
        data['section_choices'] = [dict(text=c.full_name, value=c.id) for c in Section.objects.filter(division__branch__sector__name__icontains="science")]
        data['org_choices'] = [dict(text=item.tfull, value=item.tfull) for item in Organization.objects.filter(is_dfo=True)]
        return Response(data)


class RecommendationModelMetaAPIView(APIView):
    permission_classes = [IsAuthenticated]
    model = models.Recommendation

    def get(self, request):
        data = dict()
        data['labels'] = _get_labels(self.model)
        data['decision_choices'] = [dict(text=c[1], value=c[0]) for c in model_choices.decision_choices]
        return Response(data)


class AchievementModelMetaAPIView(APIView):
    permission_classes = [IsAuthenticated]
    model = models.Achievement

    def get(self, request):
        data = dict()
        data['labels'] = _get_labels(self.model)
        data['category_choices'] = [dict(text=str(item), value=item.id) for item in models.AchievementCategory.objects.all()]
        data['publication_type_choices'] = [dict(text=str(item), value=item.id) for item in models.PublicationType.objects.all()]
        data['review_type_choices'] = [dict(text=str(item), value=item.id) for item in models.ReviewType.objects.all()]
        return Response(data)
