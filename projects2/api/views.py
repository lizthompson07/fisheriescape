from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from . import serializers
from ..models import ProjectYear


class CurrentUserAPIView(APIView):
    def get(self, request):
        serializer = serializers.UserDisplaySerializer(instance=request.user)
        return Response(serializer.data)



class ProjectYearViewSet(ModelViewSet):
    queryset = ProjectYear.objects.all().order_by("-created_at")
    # lookup_field = 'slug'
    serializer_class = serializers.ProjectYearSerializer
    permission_classes = [IsAuthenticated]

    # def perform_create(self, serializer):
    #     serializer.save(author=self.request.user)
