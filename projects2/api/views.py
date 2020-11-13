from pandas import date_range
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import RetrieveAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import permissions
from . import serializers
from .. import models, stat_holidays


class CurrentUserAPIView(APIView):
    def get(self, request):
        serializer = serializers.UserDisplaySerializer(instance=request.user)
        return Response(serializer.data)


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

    def perform_create(self, serializer):
        serializer.save(project_year_id=self.kwargs.get("project_year"))

    # def post(self, request, *args, **kwargs):
    #     super().post(request, *args, **kwargs)


class StaffRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = models.Staff.objects.all()
    serializer_class = serializers.StaffSerializer
    permission_classes = [permissions.CanModifyOrReadOnly]
