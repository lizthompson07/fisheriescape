from django.urls import path
from . import views
from .admin import spot_admin_site

app_name = 'spot'

urlpatterns = [
    path('close/', views.CloserTemplateView.as_view(), name="close_me"),
    path('', views.IndexTemplateView.as_view(), name="index"),

    # SPOT-ADMIN #
    ##############
    path('spot-admin/', spot_admin_site.urls),

    # ORGANIZATION #
    ################
    path('orgs/', views.OrganizationListView.as_view(), name="org_list"),
    path('org/new/', views.OrganizationCreateView.as_view(), name="org_new"),
    path('org/<int:pk>/view/', views.OrganizationDetailView.as_view(), name="org_detail"),
    path('org/<int:pk>/edit/', views.OrganizationUpdateView.as_view(), name="org_edit"),
    path('org/<int:pk>/delete/', views.OrganizationDeleteView.as_view(), name="org_delete"),

    # PERSON #
    ##########
    path('people/', views.PersonListView.as_view(), name="person_list"),
    path('person/new/', views.PersonCreateView.as_view(), name="person_new"),
    path('person/<int:pk>/view/', views.PersonDetailView.as_view(), name="person_detail"),
    path('person/<int:pk>/edit/', views.PersonUpdateView.as_view(), name="person_edit"),
    path('person/<int:pk>/delete/', views.PersonDeleteView.as_view(), name="person_delete"),

    # PROJECT #
    ###########
    path('projects/', views.ProjectListView.as_view(), name="project_list"),
    path('project/new/', views.ProjectCreateView.as_view(), name="project_new"),
    path('project/<int:pk>/view/', views.ProjectDetailView.as_view(), name="project_detail"),
    path('project/<int:pk>/edit/', views.ProjectUpdateView.as_view(), name="project_edit"),
    path('project/<int:pk>/delete/', views.ProjectDeleteView.as_view(), name="project_delete"),

    # Objectives #
    ##############
    path('objs/', views.ObjectiveListView.as_view(), name="obj_list"),
    path('obj/new/', views.ObjectiveCreateView.as_view(), name="obj_new"),
    path('obj/<int:pk>/view/', views.ObjectiveDetailView.as_view(), name="obj_detail"),
    path('obj/<int:pk>/edit/', views.ObjectiveUpdateView.as_view(), name="obj_edit"),
    path('obj/<int:pk>/delete/', views.ObjectiveDeleteView.as_view(), name="obj_delete"),

    # Methods #
    ###########
    path('meths/', views.MethodListView.as_view(), name="meth_list"),
    path('meth/new/', views.MethodCreateView.as_view(), name="meth_new"),
    path('meth/<int:pk>/view/', views.MethodDetailView.as_view(), name="meth_detail"),
    path('meth/<int:pk>/edit/', views.MethodUpdateView.as_view(), name="meth_edit"),
    path('meth/<int:pk>/delete/', views.MethodDeleteView.as_view(), name="meth_delete"),

    # Databases #
    #############
    path('datas/', views.DataListView.as_view(), name="data_list"),
    path('data/new/', views.DataCreateView.as_view(), name="data_new"),
    path('data/<int:pk>/view/', views.DataDetailView.as_view(), name="data_detail"),
    path('data/<int:pk>/edit/', views.DataUpdateView.as_view(), name="data_edit"),
    path('data/<int:pk>/delete/', views.DataDeleteView.as_view(), name="data_delete"),

    # Feedback #
    #############
    path('feedbacks/', views.FeedbackListView.as_view(), name="feedback_list"),
    path('feedback/new/', views.FeedbackCreateView.as_view(), name="feedback_new"),
    path('feedback/<int:pk>/view/', views.FeedbackDetailView.as_view(), name="feedback_detail"),
    path('feedback/<int:pk>/delete/', views.FeedbackDeleteView.as_view(), name="feedback_delete"),

    # Databases #
    #############
    path('meetings/', views.MeetingsListView.as_view(), name="meetings_list"),
    path('meeting/new/', views.MeetingsCreateView.as_view(), name="meetings_new"),
    path('meeting/<int:pk>/view/', views.MeetingsDetailView.as_view(), name="meetings_detail"),
    path('meeting/<int:pk>/edit/', views.MeetingsUpdateView.as_view(), name="meetings_edit"),
    path('meeting/<int:pk>/delete/', views.MeetingsDeleteView.as_view(), name="meetings_delete"),

    # Reports #
    ###########
    path('reports/', views.ReportsListView.as_view(), name="reports_list"),
    path('report/new/', views.ReportsCreateView.as_view(), name="reports_new"),
    path('report/<int:pk>/view/', views.ReportsDetailView.as_view(), name="reports_detail"),
    path('report/<int:pk>/edit/', views.ReportsUpdateView.as_view(), name="reports_edit"),
    path('report/<int:pk>/delete/', views.ReportsDeleteView.as_view(), name="reports_delete"),

]
