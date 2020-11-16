from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'projects2'

urlpatterns = [
    path('', views.IndexTemplateView.as_view(), name="index"),

    # PROJECTS #
    ############

    path('projects/new/', views.ProjectCreateView.as_view(), name="project_new"),
    path('projects/<int:pk>/view/', views.ProjectDetailView.as_view(), name="project_detail"),
    path('projects/<int:pk>/edit/', views.ProjectUpdateView.as_view(), name="project_edit"),
    path('projects/<int:pk>/delete/', views.ProjectDeleteView.as_view(), name="project_delete"),
    path('admin/projects/all/', views.ProjectListView.as_view(), name="project_list"),


    # PROJECT YEAR #
    ################
    path('projects/<int:project>/new-project-year/', views.ProjectYearCreateView.as_view(), name="year_new"),
    path('project-year/<int:pk>/edit/', views.ProjectYearUpdateView.as_view(), name="year_edit"),
    path('project-year/<int:pk>/delete/', views.ProjectYearDeleteView.as_view(), name="year_delete"),
    path('project-year/<int:pk>/clone/', views.ProjectYearCloneView.as_view(), name="year_clone"),


###################################

    # path('all/', views.ProjectListView.as_view(), name="project_list"),

    path('my-list/', views.MyProjectListView.as_view(), name="my_project_list"),
    path('project/<int:pk>/print/', views.ProjectPrintDetailView.as_view(), name="project_print"),
    path('project/<int:pk>/delete/popout/<int:pop>/', views.ProjectDeleteView.as_view(), name="project_delete"),
    path('project/<int:pk>/submit/', views.ProjectSubmitUpdateView.as_view(), name="project_submit"),
    path('project/<int:pk>/submit/popout/<int:pop>/', views.ProjectSubmitUpdateView.as_view(), name="project_submit"),
    path('project/<int:pk>/notes/', views.ProjectNotesUpdateView.as_view(), name="project_notes"),
    # path('project/<int:pk>/clone/', views.ProjectCloneUpdateView.as_view(), name="project_clone"),
    # path('approval/project/<int:pk>/', views.ProjectApprovalUpdateView.as_view(), name="project_approve"),
    # path('recommendation/project/<int:pk>/', views.ProjectRecommendationUpdateView.as_view(), name="project_recommend"),

    # management views
    ################
    path('section/<int:section>/', views.SectionProjectListView.as_view(), name="section_project_list"),
    path('project/<int:pk>/overview/', views.ProjectOverviewDetailView.as_view(), name="project_overview"),
    path('project/<int:pk>/overview/popout/<int:pop>/', views.ProjectOverviewDetailView.as_view(), name="project_overview"),

    # STAFF #
    #########
    path('project/<int:project>/staff/new/', views.StaffCreateView.as_view(), name="staff_new"),
    path('staff/<int:pk>/edit/', views.StaffUpdateView.as_view(), name="staff_edit"),
    path('staff/<int:pk>/delete/', views.staff_delete, name="staff_delete"),
    path('staff/<int:pk>/overtime-calculator/', views.OverTimeCalculatorTemplateView.as_view(), name="ot_calc"),

    # # FILES #
    # #########
    # path('project/<int:project>/file/new/', views.FileCreateView.as_view(), name='file_new'),
    # path('project/<int:project>/file/new/status-report/<int:status_report>/', views.FileCreateView.as_view(), name='file_new'),
    # path('file/<int:pk>/view/', views.FileDetailView.as_view(), name='file_detail'),
    # path('file/<int:pk>/edit/', views.FileUpdateView.as_view(), name='file_edit'),
    # path('file/<int:pk>/delete/', views.FileDeleteView.as_view(), name='file_delete'),
    #
    # # STATUS REPORT #
    # #################
    # path('project/<int:project>/status-report/new/', views.StatusReportCreateView.as_view(), name="report_new"),
    # path('status-report/<int:pk>/edit/', views.StatusReportUpdateView.as_view(), name="report_edit"),
    # path('status-report/<int:pk>/delete/', views.StatusReportDeleteView.as_view(), name="report_delete"),
    # path('status-report/<int:pk>/pdf/', views.StatusReportPrintDetailView.as_view(), name="report_print"),
    #
    # # MILESTONE UPDATE #
    # ####################
    # path('milestone-update/<int:pk>/edit/', views.MilestoneUpdateUpdateView.as_view(), name="milestone_update_edit"),
    #
    #
    # # SETTINGS #
    # ############
    path('settings/funding-sources/', views.FundingSourceFormsetView.as_view(), name="manage_funding_sources"),
    path('settings/funding-source/<int:pk>/delete/', views.FundingSourceHardDeleteView.as_view(), name="delete_funding_source"),

    path('settings/activity-types/', views.ActivityTypeFormsetView.as_view(), name="manage_activity_types"),
    path('settings/activity-type/<int:pk>/delete/', views.ActivityTypeHardDeleteView.as_view(), name="delete_activity_type"),

    path('settings/om-categories/', views.OMCategoryFormsetView.as_view(), name="manage_om_cats"),
    path('settings/om-category/<int:pk>/delete/', views.OMCategoryHardDeleteView.as_view(), name="delete_om_cat"),

    path('settings/employee-types/', views.EmployeeTypeFormsetView.as_view(), name="manage_employee_types"),
    path('settings/employee-type/<int:pk>/delete/', views.EmployeeTypeHardDeleteView.as_view(), name="delete_employee_type"),

    # path('settings/statuses/', views.StatusFormsetView.as_view(), name="manage_statuses"),
    # path('settings/status/<int:pk>/delete/', views.StatusHardDeleteView.as_view(), name="delete_status"),

    path('settings/tags/', views.TagFormsetView.as_view(), name="manage_tags"),
    path('settings/tag/<int:pk>/delete/', views.TagHardDeleteView.as_view(), name="delete_tag"),

    path('settings/help-texts/', views.HelpTextFormsetView.as_view(), name="manage_help_text"),
    path('settings/help-text/<int:pk>/delete/', views.HelpTextHardDeleteView.as_view(), name="delete_help_text"),

    path('settings/levels/', views.LevelFormsetView.as_view(), name="manage_levels"),
    path('settings/level/<int:pk>/delete/', views.LevelHardDeleteView.as_view(), name="delete_level"),

    # # path('settings/programs/', views.ProgramFormsetView.as_view(), name="manage_programs"),
    # # path('settings/program/<int:pk>/delete/', views.ProgramHardDeleteView.as_view(), name="delete_program"),

    path('settings/themes/', views.ThemeFormsetView.as_view(), name="manage_themes"),
    path('settings/theme/<int:pk>/delete/', views.ThemeHardDeleteView.as_view(), name="delete_theme"),

    path('settings/upcoming-dates/', views.UpcomingDateFormsetView.as_view(), name="manage-upcoming-dates"),
    path('settings/upcoming-date/<int:pk>/delete/', views.UpcomingDateHardDeleteView.as_view(), name="delete-upcoming-date"),

    path('settings/reference-materials/', views.ReferenceMaterialListView.as_view(), name="ref_mat_list"),
    path('settings/reference-materials/new/', views.ReferenceMaterialCreateView.as_view(), name="ref_mat_new"),
    path('settings/reference-materials/<int:pk>/edit/', views.ReferenceMaterialUpdateView.as_view(), name="ref_mat_edit"),
    path('settings/reference-materials/<int:pk>/delete/', views.ReferenceMaterialDeleteView.as_view(), name="ref_mat_delete"),

    path('settings/functional-groups/', views.FunctionalGroupListView.as_view(), name="group_list"),
    path('settings/functional-group/new/', views.FunctionalGroupCreateView.as_view(), name="group_new"),
    path('settings/functional-group/<int:pk>/edit/', views.FunctionalGroupUpdateView.as_view(), name="group_edit"),
    path('settings/functional-group/<int:pk>/delete/', views.FunctionalGroupDeleteView.as_view(), name="group_delete"),

    #
    # path('admin/staff-list/', views.AdminStaffListView.as_view(), name="admin_staff_list"),
    # path('admin/staff/<int:pk>/edit/<str:qry>/', views.AdminStaffUpdateView.as_view(), name="admin_staff_edit"),
    # path('admin/staff/<int:pk>/edit/', views.AdminStaffUpdateView.as_view(), name="admin_staff_edit"),
    #
    # path('admin/submitted-unapproved-list/', views.SubmittedUnapprovedProjectsListView.as_view(), name="admin_submitted_unapproved"),
    #
    # # project approvals
    # path('admin/project-approvals/search/', views.ProjectApprovalsSearchView.as_view(), name="admin_project_approval_search"),
    # path('admin/project-approval-for/region/<int:region>/fiscal-year/<int:fy>/', views.ProjectApprovalFormsetView.as_view(), name="admin_project_approval"),
    #
    #
    # # Reports #
    # ###########
    # path('reports/search/', views.ReportSearchFormView.as_view(), name="report_search"),
    # path(
    #     'reports/master-spreadsheet/fiscal-year/<int:fiscal_year>/regions/<str:regions>/divisions/<str:divisions>/sections/<str:sections>/',
    #     views.master_spreadsheet, name="report_master"),
    # path('reports/project-summary/fiscal-year/<int:fiscal_year>/regions/<str:regions>/divisions/<str:divisions>/sections/<str:sections>/',
    #      views.PDFProjectSummaryReport.as_view(), name="pdf_project_summary"),
    # path(
    #     'reports/batch-workplan-export/fiscal-year/<int:fiscal_year>/regions/<str:regions>/divisions/<str:divisions>/sections/<str:sections>/',
    #     views.PDFProjectPrintoutReport.as_view(), name="pdf_printout"),
    #
    # # this is a special view of the masterlist report that is called from the my_section view
    # path('reports/section-head-spreadsheet/fiscal-year/<int:fiscal_year>/user/<int:user>', views.master_spreadsheet, name="report_sh"),
    #
    # path('reports/export-program-list/', views.export_program_list, name="export_program_list"),
    #
    # # GULF REGION REPORTS
    # path('reports/FTE_summary/fiscal-year/<int:fiscal_year>/regions/<str:regions>/divisions/<str:divisions>/sections/<str:sections>/',
    #      views.PDFFTESummaryReport.as_view(), name="pdf_fte_summary"),
    # path('reports/OT/fiscal-year/<int:fiscal_year>/regions/<str:regions>/divisions/<str:divisions>/sections/<str:sections>/',
    #      views.PDFOTSummaryReport.as_view(), name="pdf_ot"),
    # path('reports/costs/fiscal-year/<int:fiscal_year>/regions/<str:regions>/divisions/<str:divisions>/sections/<str:sections>/',
    #      views.PDFCostSummaryReport.as_view(), name="pdf_costs"),
    # path('reports/collaborators/fiscal-year/<int:fiscal_year>/regions/<str:regions>/divisions/<str:divisions>/sections/<str:sections>/',
    #      views.PDFCollaboratorReport.as_view(), name="pdf_collab"),
    # path('reports/agreements/fiscal-year/<int:fiscal_year>/regions/<str:regions>/divisions/<str:divisions>/sections/<str:sections>/',
    #      views.PDFAgreementsReport.as_view(), name="pdf_agreements"),
    # path('reports/dougs-report/fiscal-year/<int:fiscal_year>/regions/<str:regions>/divisions/<str:divisions>/sections/<str:sections>/',
    #      views.dougs_spreadsheet, name="doug_report"),
    # path('reports/data-management/fiscal-year/<int:fiscal_year>/regions/<str:regions>/divisions/<str:divisions>/sections/<str:sections>/',
    #      views.PDFDataReport.as_view(), name="pdf_data"),
    # path('reports/sara-report/fiscal-year/<int:fiscal_year>/funding/<int:funding>/regions/<str:regions>/divisions/<str:divisions>/sections/<str:sections>',
    #      views.PDFFundingReport.as_view(), name="pdf_funding"),
    # path('reports/sara-report/fiscal-year/<int:fiscal_year>/funding/<int:funding>/regions/<str:regions>/divisions/<str:divisions>/sections/<str:sections>/',
    #      views.funding_spreadsheet, name="xls_funding"),
    # path('reports/sara-report/fiscal-year/<int:fiscal_year>/funding/<int:funding>/regions/<str:regions>/divisions/<str:divisions>/sections/<str:sections>/omcatagory/<str:omcatagory>/',
    #      views.funding_spreadsheet, name="xls_funding_by_om"),
    # path('reports/covid/fiscal-year/<int:fiscal_year>/regions/<str:regions>/divisions/<str:divisions>/sections/<str:sections>/',
    #      views.covid_spreadsheet, name="xls_covid"),
    # # path('reports/workplan-summary/fiscal-year/<int:fiscal_year>', views.workplan_summary, name="workplan_summary"),
    #
    # # INTERACTIVE WORKPLANS #
    # #########################
    # path('interactive-workplan/region/<int:region>/division/<int:division>/section/<int:section>/year/<int:fiscal_year>/type/<str:type>/', views.IWGroupList.as_view(),
    #      name="iw_group_list"),
    #
    # # by section / program by fgroup
    # path('interactive-workplan/<int:fiscal_year>/region/<int:region>/division/<int:division>/section/<int:section>/small-item/<int:small_item>/group/<int:group>/projects/type/<str:type>/',
    #      views.IWProjectList.as_view(), name="iw_project_list"),
    # # by section / program
    # path('interactive-workplan/<int:fiscal_year>/region/<int:region>/division/<int:division>/section/<int:section>/small-item/<int:small_item>/projects/type/<str:type>/',
    #      views.IWProjectList.as_view(), name="iw_project_list"),
    #
    # path('note/<int:pk>/edit/', views.NoteUpdateView.as_view(), name="note_edit"),

]