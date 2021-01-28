from django.urls import path

from . import views

urlpatterns = [
    path("scuba/user/", views.CurrentUserAPIView.as_view(), name="current-user"),  # tested

    # observations
    path("scuba/observations/", views.ObservationListCreateAPIView.as_view(), name="observation-list"),  # tested
    path("scuba/observations/<int:pk>/", views.ObservationRetrieveUpdateDestroyAPIView.as_view(), name="observation-detail"),  # tested
    path("scuba/sections/", views.SectionListCreateAPIView.as_view(), name="section-list"),  # tested
    path("scuba/sections/<int:pk>/", views.SectionRetrieveUpdateDestroyAPIView.as_view(), name="section-detail"),  # tested

]
