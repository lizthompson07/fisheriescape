from django.conf.urls import url
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


# urlpatterns = [
#     url(r'^$', views.index, name='index'),
# ]

app_name = 'ios2'

urlpatterns = [
    path('close/', views.CloserTemplateView.as_view(), name="close_me"),
    path('', views.IndexTemplateView.as_view(), name="index"),

    # PROJECTS #
    ############
    # path('my-list/', views.MyProjectListView.as_view(), name="my_project_list"),
    # path('my-section/', views.MySectionListView.as_view(), name="my_section_list"),
    path('ios2/', views.InstrumentListView.as_view(), name="instrument_list"),
    path('ios2/new/', views.InstrumentCreateView.as_view(), name="instrument_new"),
    path('ios2/<int:pk>/view', views.InstrumentDetailView.as_view(), name="instrument_detail"),
    path('ios2/<int:pk>/submit', views.InstrumentSubmitUpdateView.as_view(), name="instrument_submit"),
    path('ios2/<int:pk>/print', views.InstrumentPrintDetailView.as_view(), name="instrument_print"),
    path('ios2/<int:pk>/delete', views.InstrumentDeleteView.as_view(), name="instrument_delete"),
    path('ios2/<int:pk>/edit', views.InstrumentUpdateView.as_view(), name="instrument_edit"),

    path('ios2/mlist', views.MooringListView.as_view(), name="mooring_list"),

    # InstrumentDeployments #
    ############
    path('ios2/<int:instrument>/instrudeployment/new/', views.InstrumentDeploymentCreateView.as_view(),
         name="instrudeploy_new"),
    path('instrudeployment/<int:pk>/populate-all/', views.deployment_populate, name="deployment_populate"),
    path('instrudeployment/<int:pk>/edit/', views.DeploymentUpdateView.as_view(), name="deployment_edit"),
    path('instrudeployment/<int:pk>/delete/', views.deployment_delete, name="deployment_delete"),
    path('ios2/<int:instrument>/clear-empty/', views.deployment_clear, name="deployment_clear"),
    path('instrudeployment/<int:pk>/view', views.DeploymentDetailView.as_view(), name="deployment_detail"),
    # path('staff/<int:pk>/edit/', views.StaffUpdateView.as_view(), name="staff_edit"),

    # # Deployments #
    # ############
    path('ios2/<int:instrument>/deployment/new/', views.DeploymentCreateView.as_view(), name="deploy_new"),
    path('deployment/<int:pk>/populate-all/', views.deployment_populate, name="deployment_populate"),
    path('deployment/<int:pk>/edit/', views.DeploymentUpdateView.as_view(), name="deployment_edit"),
    path('deployment/<int:pk>/delete/', views.deployment_delete, name="deployment_delete"),
    path('ios2/<int:instrument>/clear-empty/', views.deployment_clear, name="deployment_clear"),
    path('deployment/<int:pk>/view', views.DeploymentDetailView.as_view(), name="deployment_detail"),
]
