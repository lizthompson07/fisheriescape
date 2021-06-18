from django.urls import path

from . import views

urlpatterns = [
    path("scuba/user/", views.CurrentUserAPIView.as_view(), name="scuba-current-user"),  # tested

    # observations
    path("scuba/observations/", views.ObservationListCreateAPIView.as_view(), name="scuba-observation-list"),  # tested
    path("scuba/observations/<int:pk>/", views.ObservationRetrieveUpdateDestroyAPIView.as_view(), name="scuba-observation-detail"),  # tested
    path("scuba/sections/", views.SectionListCreateAPIView.as_view(), name="scuba-section-list"),  # tested
    path("scuba/sections/<int:pk>/", views.SectionRetrieveUpdateDestroyAPIView.as_view(), name="scuba-section-detail"),  # tested

]
