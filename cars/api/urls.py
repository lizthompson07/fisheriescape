from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# router = DefaultRouter()
# router.register(r'reservations', views.CSASRequestViewSet)


urlpatterns = [
    # path("cars/", include(router.urls)),
    path("field-work/reservations-for-calendar/", views.CalendarRSVPListAPIView.as_view(), name="cars-rsvp-cal"),


]
