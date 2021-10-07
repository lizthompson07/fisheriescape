from django.urls import path

from . import views

urlpatterns = [
    path("resup/user/", views.CurrentUserAPIView.as_view(), name="scuba-current-user"),  # tested

    # observations
    path("ressub/observations/", views.ObservationListCreateAPIView.as_view(), name="scuba-observation-list"),  # tested
    path("ressub/observations/<int:pk>/", views.ObservationRetrieveUpdateDestroyAPIView.as_view(), name="scuba-observation-detail"),  # tested
    path("ressub/sections/", views.SectionListCreateAPIView.as_view(), name="scuba-section-list"),  # tested
    path("ressub/sections/<int:pk>/", views.SectionRetrieveUpdateDestroyAPIView.as_view(), name="scuba-section-detail"),  # tested

]
