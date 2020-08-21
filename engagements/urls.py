from django.urls import path
from . import views

app_name = 'engagements'

urlpatterns = [
    path('', views.engagements_home, name='home'),

    # Organizations
    path('organizations/', views.OrganizationListView.as_view(), name='organization_list'),
    path('organizations/add', views.OrganizationCreateView.as_view(), name='organization_create'),
    path('organizations/<slug:slug>', views.OrganizationDetailView.as_view(), name='organization_detail'),
    path('organizations/<slug:slug>/edit', views.OrganizationUpdateView.as_view(), name='organization_update'),
    path('organizations/<slug:slug>/delete', views.OrganizationDeleteView.as_view(), name='organization_delete'),
]
