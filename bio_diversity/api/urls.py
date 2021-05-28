from django.urls import path

from . import views

urlpatterns = [
    path("bio_diversity/user/", views.BioCurrentUserAPIView.as_view(), name="bio-current-user"),  # tested

    path("bio_diversity/indv/", views.IndividualAPIView.as_view(), name="api-indv"),  # tested
    path("bio_diversity/cup/", views.CupAPIView.as_view(), name="api-cup"),  # tested
    path("bio_diversity/anix/", views.AnixAPIView.as_view(), name="api-anix"),  # tested
    path("bio_diversity/contx/", views.ContxAPIView.as_view(), name="api-contx"),  # tested
    path("bio_diversity/cnt/", views.CountAPIView.as_view(), name="api-cnt"),  # tested
    path("bio_diversity/grp/", views.GroupAPIView.as_view(), name="api-grp"),  # tested

]
