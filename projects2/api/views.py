from rest_framework.generics import RetrieveAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from . import serializers
from . import permissions
from .. import models


class CurrentUserAPIView(APIView):
    def get(self, request):
        serializer = serializers.UserDisplaySerializer(instance=request.user)
        return Response(serializer.data)


class ProjectYearRetrieveAPIView(RetrieveAPIView):
    queryset = models.ProjectYear.objects.all().order_by("-created_at")
    serializer_class = serializers.ProjectYearSerializer
    permission_classes = [IsAuthenticated]


class StaffListCreateAPIView(ListCreateAPIView):
    queryset = models.Staff.objects.all()
    serializer_class = serializers.StaffSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        year = models.ProjectYear.objects.get(pk=self.kwargs.get("project_year"))
        return year.staff_set.all()


class StaffRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = models.Staff.objects.all()
    serializer_class = serializers.StaffSerializer
    permission_classes = [permissions.CanModifyOrReadOnly]

