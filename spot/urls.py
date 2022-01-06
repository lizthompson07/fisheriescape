from django.urls import path

from . import views

app_name = 'spot'

urlpatterns = [
    path('', views.IndexTemplateView.as_view(), name="index"),

    # URLS
    # user permissions
    path('settings/users/', views.SpotUserFormsetView.as_view(), name="manage_spot_users"),
    path('settings/users/<int:pk>/delete/', views.SpotUserHardDeleteView.as_view(), name="delete_spot_user"),

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
    path('projects/download-project-csv', views.export_project, name="export_project"),

    # Objectives #
    ##############
    path('objs/', views.ObjectiveListView.as_view(), name="obj_list"),
    path('project/<int:project>/obj/new/', views.ObjectiveCreateView.as_view(), name="obj_new"),
    path('obj/<int:pk>/view/', views.ObjectiveDetailView.as_view(), name="obj_detail"),
    path('obj/<int:pk>/edit/', views.ObjectiveUpdateView.as_view(), name="obj_edit"),
    path('obj/<int:pk>/delete/', views.ObjectiveDeleteView.as_view(), name="obj_delete"),
    path('objs/download-objective-csv', views.export_objective, name="export_objective"),

    # Methods #
    ###########
    path('meths/', views.MethodListView.as_view(), name="meth_list"),
    path('project/<int:project>/meth/new/', views.MethodCreateView.as_view(), name="meth_new"),
    path('meth/<int:pk>/view/', views.MethodDetailView.as_view(), name="meth_detail"),
    path('meth/<int:pk>/edit/', views.MethodUpdateView.as_view(), name="meth_edit"),
    path('meth/<int:pk>/delete/', views.MethodDeleteView.as_view(), name="meth_delete"),
    path('meths/download-method-csv', views.export_method, name="export_method"),

    # Databases #
    #############
    path('datas/', views.DataListView.as_view(), name="data_list"),
    path('project/<int:project>/data/new/', views.DataCreateView.as_view(), name="data_new"),
    path('data/<int:pk>/view/', views.DataDetailView.as_view(), name="data_detail"),
    path('data/<int:pk>/edit/', views.DataUpdateView.as_view(), name="data_edit"),
    path('data/<int:pk>/delete/', views.DataDeleteView.as_view(), name="data_delete"),
    path('datas/download-data-csv', views.export_data, name="export_data"),

    # Feedback #
    #############
    path('feedbacks/', views.FeedbackListView.as_view(), name="feedback_list"),
    path('feedback/new/', views.FeedbackCreateView.as_view(), name="feedback_new"),
    path('feedback/<int:pk>/view/', views.FeedbackDetailView.as_view(), name="feedback_detail"),
    path('feedback/<int:pk>/delete/', views.FeedbackDeleteView.as_view(), name="feedback_delete"),

    # Meetings #
    #############
    path('meetings/', views.MeetingsListView.as_view(), name="meetings_list"),
    path('meeting/new/', views.MeetingsCreateView.as_view(), name="meetings_new"),
    path('meeting/<int:pk>/view/', views.MeetingsDetailView.as_view(), name="meetings_detail"),
    path('meeting/<int:pk>/edit/', views.MeetingsUpdateView.as_view(), name="meetings_edit"),
    path('meeting/<int:pk>/delete/', views.MeetingsDeleteView.as_view(), name="meetings_delete"),

    # Reports #
    ###########
    path('reports/', views.ReportsListView.as_view(), name="reports_list"),
    path('project/<int:project>/report/new/', views.ReportsCreateView.as_view(), name="reports_new"),
    path('report/<int:pk>/view/', views.ReportsDetailView.as_view(), name="reports_detail"),
    path('report/<int:pk>/edit/', views.ReportsUpdateView.as_view(), name="reports_edit"),
    path('report/<int:pk>/delete/', views.ReportsDeleteView.as_view(), name="reports_delete"),
    path('reports/download-reports-csv', views.export_reports, name="export_reports"),

    # Objective Data Type Quality #
    ###############################
    path('obj/<int:obj>/objectivedatatypequality/new/', views.ObjectiveDataTypeQualityCreateView.as_view(), name="objectivedatatypequality_new"),
    path('objectivedatatypequality/<int:pk>/edit/', views.ObjectiveDataTypeQualityUpdateView.as_view(), name="objectivedatatypequality_edit"),
    path('objectivedatatypequality/<int:pk>/delete/', views.ObjectiveDataTypeQualityDeleteView.as_view(), name="objectivedatatypequality_delete"),

    # Objective Outcome #
    ###############################
    path('obj/<int:obj>/objectiveoutcome/new/', views.ObjectiveOutcomeCreateView.as_view(), name="objectiveoutcome_new"),
    path('objectiveoutcome/<int:pk>/edit/', views.ObjectiveOutcomeUpdateView.as_view(), name="objectiveoutcome_edit"),
    path('objectiveoutcome/<int:pk>/delete/', views.ObjectiveOutcomeDeleteView.as_view(), name="objectiveoutcome_delete"),

    # River #
    ##########
    path('rivers/', views.RiverListView.as_view(), name="river_list"),
    path('river/new/', views.RiverCreateView.as_view(), name="river_new"),
    path('river/<int:pk>/view/', views.RiverDetailView.as_view(), name="river_detail"),
    path('river/<int:pk>/edit/', views.RiverUpdateView.as_view(), name="river_edit"),
    path('river/<int:pk>/delete/', views.RiverDeleteView.as_view(), name="river_delete"),

    # Watershed #
    ##########
    path('watersheds/', views.WaterShedListView.as_view(), name="watershed_list"),
    path('watershed/new/', views.WaterShedCreateView.as_view(), name="watershed_new"),
    path('watershed/<int:pk>/view/', views.WaterShedDetailView.as_view(), name="watershed_detail"),
    path('watershed/<int:pk>/edit/', views.WaterShedUpdateView.as_view(), name="watershed_edit"),
    path('watershed/<int:pk>/delete/', views.WaterShedDeleteView.as_view(), name="watershed_delete"),

    # LakeSystem #
    ##########
    path('lakesystems/', views.LakeSystemListView.as_view(), name="lakesystem_list"),
    path('lakesystem/new/', views.LakeSystemCreateView.as_view(), name="lakesystem_new"),
    path('lakesystem/<int:pk>/view/', views.LakeSystemDetailView.as_view(), name="lakesystem_detail"),
    path('lakesystem/<int:pk>/edit/', views.LakeSystemUpdateView.as_view(), name="lakesystem_edit"),
    path('lakesystem/<int:pk>/delete/', views.LakeSystemDeleteView.as_view(), name="lakesystem_delete"),

    # Funding Year #
    ################
    path('project/<int:project>/fundingyear/new/', views.FundingYearCreateView.as_view(), name="fundingyear_new"),
    path('fundingyear/<int:pk>/edit/', views.FundingYearUpdateView.as_view(), name="fundingyear_edit"),
    path('fundingyear/<int:pk>/delete/', views.FundingYearDeleteView.as_view(), name="fundingyear_delete"),

    # Method Document #
    ###################
    path('meth/<int:meth>/methoddocument/new/', views.MethodDocumentCreateView.as_view(), name="methoddocument_new"),
    path('methoddocument/<int:pk>/edit/', views.MethodDocumentUpdateView.as_view(), name="methoddocument_edit"),
    path('methoddocument/<int:pk>/delete/', views.MethodDocumentDeleteView.as_view(), name="methoddocument_delete"),

    # Project Certified #
    #####################
    path('project/<int:project>/projectcertified/new/', views.ProjectCertifiedCreateView.as_view(), name="projectcertified_new"),
    path('projectcertified/<int:pk>/edit/', views.ProjectCertifiedUpdateView.as_view(), name="projectcertified_edit"),
    path('projectcertified/<int:pk>/delete/', views.ProjectCertifiedDeleteView.as_view(), name="projectcertified_delete"),
]
