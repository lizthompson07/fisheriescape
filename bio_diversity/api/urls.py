from django.urls import path

from . import views

urlpatterns = [
    path("bio_diversity/user/", views.BioCurrentUserAPIView.as_view(), name="bio-current-user"),  # tested

    path("bio_diversity/indv/", views.IndividualAPIView.as_view(), name="api-indv"),  # tested

]
