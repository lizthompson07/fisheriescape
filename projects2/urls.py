from django.urls import path

from . import views

app_name = 'projects2'

urlpatterns = [
    path('', views.IndexTemplateView.as_view(), name="index"),

    # PROJECTS #
    ############

    path('projects/new/', views.ProjectCreateView.as_view(), name="project_new"),  # tested
    path('projects/<int:pk>/view/', views.ProjectDetailView.as_view(), name="project_detail"),  # tested
    path('projects/<int:pk>/edit/', views.ProjectUpdateView.as_view(), name="project_edit"),  # tested
    path('projects/<int:pk>/delete/', views.ProjectDeleteView.as_view(), name="project_delete"),  # tested
    path('projects/<int:pk>/clone/', views.ProjectCloneView.as_view(), name="project_clone"),  # tested

    path('my-list/', views.MyProjectListView.as_view(), name="my_project_list"),  # tested
    path('projects/explore/', views.ExploreProjectsTemplateView.as_view(), name="explore_projects"),  # tested
    path('projects/manage/', views.ManageProjectsTemplateView.as_view(), name="manage_projects"),  # tested

    # PROJECT YEAR #
    ################
    path('projects/<int:project>/new-project-year/', views.ProjectYearCreateView.as_view(), name="year_new"),  # tested
    path('project-years/<int:pk>/edit/', views.ProjectYearUpdateView.as_view(), name="year_edit"),  # tested
    path('project-years/<int:pk>/delete/', views.ProjectYearDeleteView.as_view(), name="year_delete"),  # tested
    path('project-years/<int:pk>/clone/', views.ProjectYearCloneView.as_view(), name="year_clone"),  # tested

    # STATUS REPORT #
    #################
    path('status-reports/<int:pk>/view/', views.StatusReportDetailView.as_view(), name="report_detail"),  # tested
    path('status-reports/<int:pk>/edit/', views.StatusReportUpdateView.as_view(), name="report_edit"),# tested
    path('status-reports/<int:pk>/review/', views.StatusReportReviewUpdateView.as_view(), name="report_review"),# tested
    path('status-reports/<int:pk>/delete/', views.StatusReportDeleteView.as_view(), name="report_delete"),# tested
    path('status-reports/<int:pk>/pdf/', views.StatusReportPrintDetailView.as_view(), name="report_pdf"),# tested

    # # SETTINGS #
    # ############
    # formsets
    path('settings/funding-sources/', views.FundingSourceFormsetView.as_view(), name="manage_funding_sources"),
    path('settings/funding-source/<int:pk>/delete/', views.FundingSourceHardDeleteView.as_view(), name="delete_funding_source"),

    path('settings/activity-types/', views.ActivityTypeFormsetView.as_view(), name="manage_activity_types"),
    path('settings/activity-type/<int:pk>/delete/', views.ActivityTypeHardDeleteView.as_view(), name="delete_activity_type"),

    path('settings/om-categories/', views.OMCategoryFormsetView.as_view(), name="manage_om_cats"),
    path('settings/om-category/<int:pk>/delete/', views.OMCategoryHardDeleteView.as_view(), name="delete_om_cat"),

    path('settings/employee-types/', views.EmployeeTypeFormsetView.as_view(), name="manage_employee_types"),
    path('settings/employee-type/<int:pk>/delete/', views.EmployeeTypeHardDeleteView.as_view(), name="delete_employee_type"),

    path('settings/tags/', views.TagFormsetView.as_view(), name="manage_tags"),
    path('settings/tag/<int:pk>/delete/', views.TagHardDeleteView.as_view(), name="delete_tag"),

    path('settings/help-texts/', views.HelpTextFormsetView.as_view(), name="manage_help_text"),
    path('settings/help-text/<int:pk>/delete/', views.HelpTextHardDeleteView.as_view(), name="delete_help_text"),

    path('settings/levels/', views.LevelFormsetView.as_view(), name="manage_levels"),
    path('settings/level/<int:pk>/delete/', views.LevelHardDeleteView.as_view(), name="delete_level"),

    path('settings/themes/', views.ThemeFormsetView.as_view(), name="manage_themes"),
    path('settings/theme/<int:pk>/delete/', views.ThemeHardDeleteView.as_view(), name="delete_theme"),

    path('settings/upcoming-dates/', views.UpcomingDateFormsetView.as_view(), name="manage-upcoming-dates"),
    path('settings/upcoming-date/<int:pk>/delete/', views.UpcomingDateHardDeleteView.as_view(), name="delete-upcoming-date"),

    # full
    path('settings/reference-materials/', views.ReferenceMaterialListView.as_view(), name="ref_mat_list"),
    path('settings/reference-materials/new/', views.ReferenceMaterialCreateView.as_view(), name="ref_mat_new"),
    path('settings/reference-materials/<int:pk>/edit/', views.ReferenceMaterialUpdateView.as_view(), name="ref_mat_edit"),
    path('settings/reference-materials/<int:pk>/delete/', views.ReferenceMaterialDeleteView.as_view(), name="ref_mat_delete"),

    path('settings/functional-groups/', views.FunctionalGroupListView.as_view(), name="group_list"),
    path('settings/functional-group/new/', views.FunctionalGroupCreateView.as_view(), name="group_new"),
    path('settings/functional-group/<int:pk>/edit/', views.FunctionalGroupUpdateView.as_view(), name="group_edit"),
    path('settings/functional-group/<int:pk>/delete/', views.FunctionalGroupDeleteView.as_view(), name="group_delete"),

    path('settings/project-codes/', views.ProjectCodeListView.as_view(), name="project_code_list"),
    path('settings/project-codes/new/', views.ProjectCodeCreateView.as_view(), name="project_code_new"),
    path('settings/project-codes/<int:pk>/edit/', views.ProjectCodeUpdateView.as_view(), name="project_code_edit"),
    path('settings/project-codes/<int:pk>/delete/', views.ProjectCodeDeleteView.as_view(), name="project_code_delete"),

    path('settings/responsibility-centers/', views.ResponsibilityCenterListView.as_view(), name="rc_list"),
    path('settings/responsibility-centers/new/', views.ResponsibilityCenterCreateView.as_view(), name="rc_new"),
    path('settings/responsibility-centers/<int:pk>/edit/', views.ResponsibilityCenterUpdateView.as_view(), name="rc_edit"),
    path('settings/responsibility-centers/<int:pk>/delete/', views.ResponsibilityCenterDeleteView.as_view(), name="rc_delete"),

    # Reports #
    ###########
    path('projects/<int:pk>/acrdp-application/', views.export_acrdp_application, name="export_acrdp_application"),#tested
    path('projects/<int:pk>/acrdp-budget/', views.export_acrdp_budget, name="export_acrdp_budget"), #tested

]
