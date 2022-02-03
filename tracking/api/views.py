from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from dm_apps import settings
from .. import models, utils
from ..tasks import chunk_pageviews


class PageViewsAPIView(APIView):
    def post(self, request):
        if settings.IS_LINUX:
            chunk_pageviews.delay()
        else:
            chunk_pageviews()

        return Response("success!!", status=status.HTTP_200_OK)
