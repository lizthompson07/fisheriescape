from django.conf.urls import url
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


# urlpatterns = [
#     url(r'^$', views.index, name='index'),
# ]

app_name = 'polls'

urlpatterns = [
    # path('close/', views.CloserTemplateView.as_view(), name="close_me"),
    path('', views.IndexTemplateView.as_view(), name="index"),

    # PROJECTS #
    ############
    # path('my-list/', views.MyProjectListView.as_view(), name="my_project_list"),
    # path('my-section/', views.MySectionListView.as_view(), name="my_section_list"),
    path('polls/', views.InstrumentListView.as_view(), name="instrument_list"),
    path('polls/new/', views.InstrumentCreateView.as_view(), name="instrument_new"),
    path('polls/<int:pk>/view', views.InstrumentDetailView.as_view(), name="instrument_detail"),
    path('polls/<int:pk>/submit', views.InstrumentSubmitUpdateView.as_view(), name="instrument_submit"),
    path('polls/<int:pk>/print', views.InstrumentPrintDetailView.as_view(), name="instrument_print"),
    path('polls/<int:pk>/delete', views.InstrumentDeleteView.as_view(), name="instrument_delete"),
    path('polls/<int:pk>/edit', views.InstrumentUpdateView.as_view(), name="instrument_edit"),

    # Deployments #
    ############
    path('polls/<int:instrument>/deployment/new/', views.DeploymentCreateView.as_view(), name="deploy_new"),
    path('polls/<int:instrument>/populate-all/', views.deployment_populate, name="deployment_populate"),
    path('polls/<int:instrument>/edit/', views.DeploymentUpdateView.as_view(), name="deployment_edit"),
    path('polls/<int:instrument>/delete/', views.deployment_delete, name="deployment_delete"),
    path('polls/<int:instrument>/clear-empty/', views.deployment_clear, name="deployment_clear"),
]
