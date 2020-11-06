from rest_framework.response import Response
from rest_framework.views import APIView


from . import serializers


class CurrentUserAPIView(APIView):
    def get(self, request):
        serializer = serializers.UserDisplaySerializer(instance=request.user)
        return Response(serializer.data)
